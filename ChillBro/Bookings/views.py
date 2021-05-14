from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum, Count
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .helpers import *
from .constants import BookingStatus, DateFilters, ProductBookingStatus, PaymentUser
from collections import defaultdict
# libraries for generating pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
# library for generating excel
import xlwt
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsUserOwner, IsOwner, IsGet, \
    IsEmployee, IsBookingBusinessClient, IsBusinessClientEntityById, IsEmployeeEntityById, IsBookingEmployee, \
    IsBusinessClientEntities, IsEmployeeEntities
import threading


# Lock for creating a new booking or updating the booking timings
from .wrapper import get_product_id_wise_product_details, create_refund_transaction, \
    update_booking_transaction_in_payment, create_booking_transaction, get_discounted_value

_booking_lock = threading.Lock()


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_total_bookings_of_product_in_duration(product_id, start_time, end_time):
    return BookedProducts.objects.active().select_related('booking') \
        .filter(product_id=product_id) \
        .filter(~Q(booking_status=ProductBookingStatus.cancelled.value)) \
        .filter(
            Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gt=start_time)) |
            Q(Q(booking__start_time__lt=end_time) & Q(booking__end_time__gte=end_time)) |
            Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gte=end_time)) |
            Q(Q(booking__start_time__gte=start_time) & Q(booking__end_time__lte=end_time))
        )


def get_total_bookings_count_of_product_in_duration(product_id, start_time, end_time):
    bookings_count = get_total_bookings_of_product_in_duration(product_id, start_time, end_time)\
                        .aggregate(sum=Sum('quantity'))['sum']
    if bookings_count is None:
        return 0
    return bookings_count


def valid_booking_with_product_details(products_quantity, booking_products_list, start_time, end_time):
    is_valid = True
    errors = defaultdict(list)

    current_time = datetime.now()
    if current_time.strftime(get_date_format()) >= start_time:
        is_valid = False
        errors["booking"].append("Start time should be greater than current time")
    if start_time >= end_time:
        is_valid = False
        errors["booking"].append("End time should be less than start time")

    for booking_product in booking_products_list:
        if booking_product['quantity'] <= 0:
            is_valid = False
            errors[booking_product['product_id']].append("Quantity should be greater than 0")

        previous_bookings_count = get_total_bookings_count_of_product_in_duration(
            booking_product['product_id'], start_time, end_time)
        total_quantity = products_quantity[booking_product['product_id']]['quantity']

        if total_quantity - previous_bookings_count < booking_product['quantity']:
            is_valid = False
            if total_quantity - previous_bookings_count == 0:
                errors[booking_product['product_id']].append("Sorry, No products are available")
            else:
                errors[booking_product['product_id']].append(
                    "Sorry, only {} products are available".format(total_quantity - previous_bookings_count))
    return is_valid, errors


def valid_booking(booking_products_list, start_time, end_time):

    product_ids = []
    for product in booking_products_list:
        product_ids.append(product['product_id'])
    products_quantity = get_product_id_wise_product_details(product_ids)

    return valid_booking_with_product_details(products_quantity, booking_products_list, start_time, end_time)


def cancel_booking(booking):
    # TODO: refund need to be handled
    # TODO: update payment amount to be paid to business client

    booked_products = BookedProducts.objects.select_related('booking').filter(booking=booking)
    booked_products.update(booking_status=ProductBookingStatus.cancelled.value)

    create_refund_transaction(
        {
            'booking_id': booking.id, 'entity_id': booking.entity_id,
            'entity_type': booking.entity_type, 'refund_amount': booking.total_money,
            'booking_date': booking.booking_date, 'booking_start': booking.start_time,
            'refund_reason': "Booking Cancelled"
        }
    )

    update_booking_transaction_in_payment(booking.id, True, 0, 0, 0)


def update_booking_status(booking_id, status):
    return Bookings.objects.filter(id=booking_id).update(booking_status=status)


def get_complete_booking_details_by_ids(booking_ids):

    bookings = Bookings.objects.filter(id__in=booking_ids)
    booked_products = BookedProducts.objects.filter(booking_id__in=booking_ids)
    booking_check_ins = CheckInDetails.objects.filter(booking_id__in=booking_ids)
    booking_check_outs = CheckOutDetails.objects.filter(booking_id__in=booking_ids)

    booking_id_wise_product_ids = defaultdict(list)
    product_ids = set()
    for booked_product in booked_products:
        product_ids.add(booked_product.product_id)
        booking_id_wise_product_ids[booked_product.booking_id].append(booked_product.product_id)
    product_id_wise_product_details = get_product_id_wise_product_details(list(product_ids))

    check_in_details = {}
    for check_in in booking_check_ins:
        check_in_details[check_in.booking_id] = check_in

    check_out_details = {}
    for check_out in booking_check_outs:
        check_out_details[check_out.booking_id] = check_out

    complete_bookings_details = []
    for booking in bookings:
        booking_dict = {
            'id': booking.id,
            'entity_type': booking.entity_type,
            'booked_at': booking.booking_date,
            'booking_status':booking.booking_status
        }
        days = datetime.now() - booking.booking_date
        seconds = int(days.total_seconds())
        if seconds<60:
            booking_dict['ago'] = "1 min"
        else:
            minutes = seconds//60
            if minutes<60:
                booking_dict['ago'] = str(minutes)+" minutes"
            else:
                hours = minutes//60
                if hours<24:
                    booking_dict['ago'] = str(hours)+" hours"
                else:
                    days = hours//24
                    booking_dict['ago'] = str(days)+" days"

        check_in_flag = True
        try:
            booking_dict['check_in'] = check_in_details[booking.id].check_in
        except KeyError:
            booking_dict['check_in'] = "Booking yet to start"
            booking_dict['check_out'] = "Booking yet to start"
            check_in_flag = False

        if check_in_flag:
            try:
                booking_dict['check_out'] = check_out_details[booking.id].check_out
            except KeyError:
                booking_dict['check_out'] = "Booking yet to end"

        booking_products_details = []
        for product_id in booking_id_wise_product_ids[booking.id]:
            booking_products_details.append(product_id_wise_product_details[product_id])
        booking_dict['products'] = booking_products_details
        complete_bookings_details.append(booking_dict)
    return complete_bookings_details


def are_overlapping_time_spans(start_time1, end_time1, start_time2, end_time2):
    if start_time1 <= start_time2 < end_time1:
        return True
    if start_time1 < end_time2 <= end_time1:
        return True
    if start_time1 <= start_time2 and end_time1 >= end_time2:
        return True
    if start_time1 >= start_time2 and end_time1 <= end_time2:
        return True
    return False


def product_availability(product_id, start_time, end_time):
    booked_products = get_total_bookings_of_product_in_duration(product_id, start_time, end_time)
    if not booked_products:
        booked_products = []

    HOUR = timedelta(hours=1)
    datetime_format = get_date_format()
    hours_dic = {}

    # converting to datetime objects
    start_time = datetime.strptime(start_time, datetime_format)
    end_time = datetime.strptime(end_time, datetime_format)

    products_quantity = get_product_id_wise_product_details([product_id])

    start_hour = datetime(start_time.year, start_time.month, start_time.day, start_time.hour, 0, 0)
    end_hour = start_hour + HOUR
    while start_hour < end_time:
        start_hour_key = start_hour.strftime(datetime_format)
        end_hour_key = end_hour.strftime(datetime_format)
        hours_dic[(start_hour_key, end_hour_key)] = products_quantity[product_id]['quantity']
        start_hour = end_hour
        end_hour += HOUR

    for booked_product in booked_products:
        booking_start_time = booked_product.booking.start_time.strftime(datetime_format)
        booking_end_time = booked_product.booking.end_time.strftime(datetime_format)
        for start_hour_key, end_hour_key in hours_dic:
            if are_overlapping_time_spans(booking_start_time, booking_end_time, start_hour_key, end_hour_key):
                if hours_dic[(start_hour_key, end_hour_key)]:
                    hours_dic[(start_hour_key, end_hour_key)] -= booked_product.quantity

    availabilities = []
    for start_hour_key, end_hour_key in hours_dic:
        availability = {
            "start_hour": start_hour_key,
            "end_hour": end_hour_key,
            "available_count": hours_dic[(start_hour_key, end_hour_key)]
        }
        availabilities.append(availability)
    return Response({"availabilities": availabilities}, 200)


class GetProductAvailability(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = ProductAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        product_id = serializer.data["product_id"]
        start_time = serializer.data["start_time"]
        end_time = serializer.data["end_time"]

        return product_availability(product_id=product_id, start_time=start_time, end_time=end_time)


class GetDateFilters(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        date_filters = [date_filter.value for date_filter in DateFilters]
        return Response(date_filters, 200)


class CreateBooking(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        request.data['created_by'] = request.user
        new_booking_serializer = NewBookingSerializer(data=request.data)
        if not new_booking_serializer.is_valid():
            return Response(new_booking_serializer.errors, 400)

        product_list = request.data.pop('products', None)
        product_ids = []
        for product in product_list:
            product_ids.append(product['product_id'])

        # Get product values
        product_values = get_product_id_wise_product_details(product_ids)
        if len(product_values) != len(product_ids):
            return Response({"message": "Can't create booking", "errors": "Invalid Products"}, 400)

        is_valid, errors = valid_booking_with_product_details(
            product_values, product_list, request.data['start_time'], request.data['end_time'])
        if not is_valid:
            return Response({"message": "Can't create booking", "errors": errors}, 400)

        total_money = 0.0
        for product in product_list:
            total_money += float(product_values[product['product_id']]['price'] * product['quantity'])

        # Validate coupon and get discounted value
        entity_id = request.data['entity_id']
        if request.data['coupon'] is not None:
            coupon = get_discounted_value(
                request.data['coupon'], request.user, product_ids, entity_id, total_money)
            if not coupon['is_valid']:
                return Response({"message": "Can't create the booking", "errors": coupon['errors']}, 400)
            request.data['total_money'] = coupon['discounted_value']
        else:
            request.data['total_money'] = total_money

        # Create Booking
        payment_mode = request.data['payment_mode']
        if payment_mode == PaymentMode.cod.value:
            request.data['payment_status'] = PaymentStatus.not_required.value

        with _booking_lock:
            bookings_serializer = BookingsSerializer()
            booking = bookings_serializer.create(request.data)

            # Create booking products
            total_net_value = 0
            for product in product_list:
                product['booking'] = booking
                product["product_value"] = product_values[product['product_id']]['price']
                product['net_value'] = product_values[product['product_id']]['net_value_details']['net_price']
                total_net_value += \
                    product_values[product['product_id']]['net_value_details']['net_price'] * product['quantity']
            booked_product_serializer_object = BookedProductsSerializer()
            booked_product_serializer_object.bulk_create(product_list)

        # Create transaction for amount to be paid to entity
        if payment_mode == PaymentMode.online.value:
            # TODO: should use net value here
            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': request.data['entity_id'],
                    'entity_type': request.data['entity_type'], 'total_money': total_net_value,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.entity.value, 'paid_by': PaymentUser.myc.value
                }
            )
        else:
            # TODO: should update total values
            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': request.data['entity_id'],
                    'entity_type': request.data['entity_type'], 'total_money': request.data['total_money'],
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.entity.value, 'paid_by': PaymentUser.customer.value
                }
            )
            # TODO: should use commission value here
            create_booking_transaction(
                {
                    'booking_id': booking.id, 'entity_id': request.data['entity_id'],
                    'entity_type': request.data['entity_type'],
                    'total_money': request.data['total_money'] - total_net_value,
                    'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                    'paid_to': PaymentUser.myc.value, 'paid_by': PaymentUser.entity.value
                }
            )

        return Response({"message": "Booking created", "booking_id": booking.id}, 200)


class UserBookingsList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        self.queryset = Bookings.objects.filter(created_by=user)
        return super().get(request, *args, **kwargs)


class CancelBookingView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsOwner |
                          IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        # TODO: Should handle refund and update payment details to be payed to entity

        booking = Bookings.objects.filter(id=kwargs['booking_id'])
        if len(booking) == 0:
            return Response({"message": "Can't update booking status", "errors": "Booking does'nt exist"}, 400)

        cancelled_serializer = CancelledDetailsSerializer()
        cancelled_serializer.create(booking[0])
        cancel_booking(kwargs['booking_id'])
        booking.update(booking_status=BookingStatus.cancelled.value)
        return Response({"message": "Booking cancelled successfully"}, 200)


class BookingsStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)

    def post(self, request, *args, **kwargs):
        input_serializer = BookingStatisticsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)
        print("came")
        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        entity_id = request.data['entity_id']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            previous_from_date = previous_to_date = None
        else:
            from_date, to_date = get_time_period(date_filter)
            previous_from_date, previous_to_date = getPreviousTimePeriod(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        cancelled_bookings = CancelledDetails.objects.cancelled_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        ongoing_bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        pending_bookings = Bookings.objects.pending_bookings(entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        customer_yet_to_take_bookings = Bookings.objects \
            .yet_to_take_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        yet_to_return_bookings = Bookings.objects \
            .yet_to_return_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        customer_taken_bookings = CheckInDetails.objects \
            .customer_taken(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']
        returned_bookings = CheckOutDetails.objects \
            .returned_bookings(from_date, to_date, entity_filter, entity_id) \
            .aggregate(count=Count('id'))['count']

        received_percentage_change = cancelled_percentage_change = None
        if date_filter != "Total" and date_filter != "Custom":
            previous_receiving_bookings = Bookings.objects \
                .received_bookings(previous_from_date, previous_to_date, entity_filter, entity_id) \
                .aggregate(count=Count('id'))['count']
            previous_cancelled_bookings = CancelledDetails.objects \
                .cancelled_bookings(previous_from_date, previous_to_date, entity_filter, entity_id) \
                .aggregate(count=Count('id'))['count']

            received_percentage_change = (received_bookings - previous_receiving_bookings) / 100
            cancelled_percentage_change = (cancelled_bookings - previous_cancelled_bookings) / 100

        # TODO: Handle cases for hiding details in Frontend for different date filters
        if date_filter == "Yesterday":
            ongoing_bookings = pending_bookings = -1

        return Response(
            {
               "received": received_bookings,
                "received_percentage_change": received_percentage_change,
                "ongoing": ongoing_bookings,
                "pending": pending_bookings,
                "cancelled": cancelled_bookings,
                "cancelled_percentage_change": cancelled_percentage_change,
                "customer_yet_to_take": customer_yet_to_take_bookings,
                "yet_to_return": yet_to_return_bookings,
                'customer_taken': customer_taken_bookings,
                'returned': returned_bookings
            }, 200)


class GetBookingsStatisticsDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def post(self, request, *args, **kwargs):
        input_serializer = GetBookingsStatisticsDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        entity_id = request.data['entity_id']
        statistics_details_type = request.data['statistics_details_type']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        self.queryset = Bookings.objects.none()
        if statistics_details_type == 'ongoing_bookings':
            self.queryset = Bookings.objects.ongoing_bookings(entity_filter, entity_id)
        elif statistics_details_type == 'pending_bookings':
            self.queryset = Bookings.objects.pending_bookings(entity_filter, entity_id)
        elif statistics_details_type == 'customer_yet_to_take_bookings':
            self.queryset = Bookings.objects.yet_to_take_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'customer_yet_to_return_bookings':
            self.queryset = Bookings.objects.yet_to_return_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'customer_taken_bookings':
            booking_ids = CheckInDetails.objects \
                .customer_taken(from_date, to_date, entity_filter, entity_id)\
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)
        elif statistics_details_type == 'returned_bookings':
            booking_ids = CheckOutDetails.objects \
                .returned_bookings(from_date, to_date, entity_filter, entity_id)\
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)
        elif statistics_details_type == 'received_bookings':
            self.queryset = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
        elif statistics_details_type == 'cancelled_bookings':
            booking_ids = CancelledDetails.objects \
                .cancelled_bookings(from_date, to_date, entity_filter, entity_id)\
                .values_list('booking_id', flat=True)
            self.queryset = Bookings.objects.filter(id__in=booking_ids)

        self.queryset = self.queryset.order_by('booking_date')

        response = super().get(request, args, kwargs)
        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])
        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class CancelProductStatusView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwner | IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookedProductsSerializer

    def put(self, request, *args, **kwargs):
        # TODO: Should handle refund and update payment details to be payed to entity
        input_serializer = CancelProductStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        booking_products = BookedProducts.objects\
            .filter(booking=request.data['booking_id'], product_id=request.data['product_id'])
        if len(booking_products) == 0:
            return Response(
                {"message": "Can't cancel product booking",
                 "error": "Invalid Booking id {} or product  {} "
                    .format(request.data['booking_id'], request.data['product_id'])}, 400)

        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request,  booking)
        booking_products.update(booking_status=ProductBookingStatus.cancelled.value)

        booking_product = booking_products[0]
        create_refund_transaction(
            {
                'booking_id': booking.id, 'entity_id': booking.entity_id,
                'entity_type': booking.entity_type,
                'refund_amount': booking_product.product_value * booking_product.quantity,
                'booking_date': booking.booking_date, 'booking_start': booking.start_time,
                'refund_reason': "Booking Cancelled"
            }
        )
        update_booking_transaction_in_payment(booking.id, False,
                                              booking_product.product_value * booking_product.quantity,
                                              booking_product.net_value * booking_product.quantity,
                                              (booking_product.product_value - booking_product.net_value)
                                              * booking_product.quantity)
        booking.total_money -= booking_product.product_value
        booking.save()

        return Response({"message": "Booking product cancelled successfully"}, 200)


class GetSpecificBookingDetails(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsOwner |
                          IsBookingBusinessClient | IsBookingEmployee )

    def get(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.select_related('created_by').get(id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid Booking id"}, 400)

        self.check_object_permissions(request, booking)
        user_data = Bookings.objects.none()
        user_data.name = booking.created_by.first_name + booking.created_by.last_name
        user_data.contact_number = booking.created_by.phone_number
        user_data.email = booking.created_by
        booking.user_details = user_data

        all_products = BookedProducts.objects.filter(booking=booking)
        products = []
        for product in all_products:
            some_data_product = BookedProducts.objects.none()
            some_data_product.product_id = product.product_id
            some_data_product.quantity = product.quantity
            products.append(some_data_product)
        booking.products = products

        serializer = GetSpecificBookingDetailsSerializer(booking).data
        serializer['transaction_details'] = get_transaction_details_by_booking_id(booking.id)
        serializer['customer_review'] = get_review_by_booking_id(booking.id)
        return Response(serializer, 200)


class GetBookingDetailsView(generics.ListAPIView):
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities | IsEmployeeEntities)

    def post(self, request, *args, **kwargs):
        input_serializer = GetBookingDetailsViewSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        entity_filter = get_entity_types_filter(request.data['entity_filter'])
        status_filter = get_status_filters(request.data['status_filter'])
        entity_id = request.data['entity_id']
        from_date, to_date = get_time_period(date_filter)

        if from_date and to_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date)
                  & Q(entity_type__in=entity_filter) & Q(booking_status__in=status_filter)
                  & Q(entity_id__in=entity_id))).order_by('booking_date')
        elif from_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__gte=from_date) & Q(entity_type__in=entity_filter)
                  & Q(booking_status__in=status_filter) & Q(entity_id__in=entity_id))).order_by('booking_date')
        elif to_date:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(booking_date__lte=to_date) & Q(entity_type__in=entity_filter)
                  & Q(booking_status__in=status_filter) & Q(entity_id__in=entity_id))).order_by('booking_date')
        else:
            self.queryset = Bookings.objects.active().filter(
                Q(Q(entity_type__in=entity_filter) & Q(booking_status__in=status_filter)
                  & Q(entity_id__in=entity_id))).order_by('booking_date')

        response = super().get(request, args, kwargs)
        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])

        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class BookingStart(APIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee, IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request, booking)
        input_serializer = BookingStartSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        other_images = request.data.pop('other_images', None)
        data = request.data.dict()
        serializer = CheckInDetailsSerializer()
        check_in = serializer.create(data)

        images = []
        for each_image in other_images:
            all_other_images = {'check_in': check_in, 'image': each_image}
            images.append(all_other_images)
        other_image_serializer = CheckInImagesSerializer()
        other_image_serializer.bulk_create(images)

        update_booking_status(data['booking_id'], BookingStatus.ongoing.value)
        return Response({"message": "Booking started"}, 200)


class BookingEnd(APIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee, IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        booking = Bookings.objects.get(id=request.data['booking_id'])
        self.check_object_permissions(request, booking)
        input_serializer = BookingEndSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        data = request.data.dict()
        other_images = request.data.pop('product_images', None)
        data.pop('product_images', None)
        review = data.pop('review', None)
        rating = data.pop('rating', None)
        booking_id = request.data['booking_id']
        created_by = request.user
        business_client_review_on_customer(review, rating, booking_id, created_by)

        serializer = CheckOutDetailsSerializer()
        check_out = serializer.create(data)

        images = []
        for each_image in other_images:
            all_product_images = {'check_out': check_out, 'image': each_image}
            images.append(all_product_images)
        product_image_serializer = CheckOutImagesSerializer()
        product_image_serializer.bulk_create(images)

        update_booking_status(data['booking_id'], BookingStatus.done.value)
        return Response({"message": "Booking Ended"}, 200)


class GetBookingEndDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee, IsBookingBusinessClient | IsBookingEmployee)

    def get(self, request, *args, **kwargs):
        booking = Bookings.objects.get(id=kwargs['booking_id'])
        self.check_object_permissions(request, booking)
        try:
            check_in_object = CheckInDetails.objects.get(booking_id=kwargs['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't get booking details", "error": "Invalid booking id"}, 400)

        response_data = {
            'is_caution_deposit_collected': True,
            'caution_amount': check_in_object.caution_amount
        }

        other_images = []
        check_in_images = CheckInImages.objects.filter(check_in_id=check_in_object.id)
        for check_in_image in check_in_images:
            other_images.append(check_in_image.image.url)
        response_data['other_images'] = other_images

        return Response(response_data, 200)


class ReportCustomerForBooking(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee, IsBookingBusinessClient | IsBookingEmployee)

    def post(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(id=request.data['booking_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update details", "error:": "Invalid booking id"}, 400)

        self.check_object_permissions(request, booking)

        request.data['booking'] = booking
        report_customer = ReportCustomerSerializer()
        report_customer.create(request.data)
        return Response({"message": "Reported on customer successfully"}, 200)


class ProductStatistics(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = ProductStatisticsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        date_filter = request.data['date_filter']
        product_id = kwargs['product_id']
        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        total_products_available = get_product_details([product_id])[product_id]['quantity']

        total_products_booked = BookedProducts.objects.received_bookings_for_product(
            product_id, from_date, to_date).aggregate(count=Sum(F('quantity')))['count']
        if total_products_booked is None:
            total_products_booked = 0

        total_products_cancelled = BookedProducts.objects.cancelled_bookings_for_product(
            product_id, from_date, to_date).aggregate(count=Sum(F('quantity')))['count']
        if total_products_cancelled is None:
            total_products_cancelled = 0

        remaining_products = total_products_available - total_products_booked + total_products_cancelled

        ongoing_products = BookedProducts.objects.ongoing_bookings_for_product(
            product_id).aggregate(count=Sum(F('quantity')))['count']
        if ongoing_products is None:
            ongoing_products = 0

        return Response(
            {
                "total_products_booked": total_products_booked,
                "total_products_cancelled": total_products_cancelled,
                "remaining_products": remaining_products,
                "ongoing_products": ongoing_products
            }, 200)


class ProductStatisticsDetails(generics.ListAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def get(self, request, *args, **kwargs):
        input_serializer = ProductStatisticsDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, 400)

        product_id = kwargs['product_id']
        date_filter = request.data['date_filter']
        statistics_details_type = request.data['statistics_details_type']

        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
        else:
            from_date, to_date = get_time_period(date_filter)

        if date_filter != "Total" and from_date is None and to_date is None:
            return Response({"message": "Invalid Date Filter!!!"}, 400)

        booking_ids = []
        if statistics_details_type == "total_products_booked":
            booking_ids = BookedProducts.objects.received_bookings_for_product(
                product_id, from_date, to_date).values_list('booking_id', flat=True)
        elif statistics_details_type == "total_products_cancelled":
            booking_ids = BookedProducts.objects.cancelled_bookings_for_product(
                product_id, from_date, to_date).values_list('booking_id', flat=True)
        elif statistics_details_type == "ongoing_products":
            booking_ids = BookedProducts.objects.ongoing_bookings_for_product(product_id)\
                .values_list('booking_id', flat=True)

        self.queryset = Bookings.objects.filter(id__in=booking_ids)
        response = super().get(request, args, kwargs)

        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])
        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)

        return response


class ReportCustomerReasonsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReportCustomerReasons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class ReportCustomerReasonsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ReportCustomerReasons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class GetBookingDetailsOfProductId(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBookingBusinessClient | IsBookingEmployee)
    serializer_class = BookingsSerializer
    queryset = Bookings.objects.order_by('booking_date').all()

    def get(self, request, *args, **kwargs):
        booking_ids = BookedProducts.objects.select_related('booking') \
            .filter(product_id=kwargs['product_id']).values_list('booking_id', flat=True)
        self.queryset = Bookings.objects.filter(id__in=booking_ids)
        response = super().get(request, args, kwargs)

        booking_ids = []
        for booking in response.data["results"]:
            booking_ids.append(booking["id"])

        response.data["results"] = get_complete_booking_details_by_ids(booking_ids)
        return response


class GeneratePDF(APIView):

    def get(self, request, *args, **kwargs):
        bookings = Bookings.objects.all()

        all_data = {'total_length': len(bookings)}
        booking_details = []
        for booking in bookings:
            data = {
                'booking_id': booking.id,
                'booking_date': booking.booking_date,
                'booking_status': booking.booking_status,
            }
            booking_details.append(data)
        all_data['data'] = booking_details
        pdf = render_to_pdf('pdf.html', all_data)

        # force download
        if pdf:
            response = Response(pdf, content_type='application/pdf')
            filename = "bookings%s.pdf" % (data['booking_id'])
            # content = "inline; filename='%s'" % (filename)
            content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return Response({"message": "Not able to generate PDF", "error": "Not able to generate PDF"}, 400)


class GenerateExcel(APIView):

    def get(self, request, *args, **kwargs):
        response = Response(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=excel_example' + str(datetime.now()) + '.xls'
        wb = xlwt.Workbook(encoding='utf-8')

        ws = wb.add_sheet('Expenses')
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Booking Id', 'Booking Date', 'Booking Status']
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = Bookings.objects.all().values_list('id', 'booking_date', 'booking_status')

        for row in rows:
            row_num += 1

            for col_num in range(3):
                ws.write(row_num, col_num, str(row[col_num]), font_style)

        wb.save(response)
        return response


class BusinessClientProductCancellationDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = BusinessClientProductCancellationSerializer(data=request.data)
        if input_serializer.is_valid():
            booked_product = BookedProducts.objects.filter(booking = request.data['booking_id'],\
                                                           product_id=request.data['product_id'])
            if len(booked_product) == 0:
                return Response({"message": "Can't cancel the product", "errors":"There is no product{}in booking id {}"\
                                .format(request.data['product_id'],request.data['booking_id'])},400)
            request.data['cancelled_by'] = request.user.id
            input_serializer.save()
            booked_product.update(booking_status= ProductBookingStatus.cancelled.value)
            return Response({"message": "Successfully cancelled the product"},200)

        else:
            return Response({"message":"Can't cancel the product","errors":input_serializer.errors},400)
