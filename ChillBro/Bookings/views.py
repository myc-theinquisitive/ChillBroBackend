from django.db.models import Q, F, FloatField, Sum
from django.utils.datetime_safe import strftime
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *
from .wrapper import *
from datetime import timedelta, date, datetime
from .helpers import *
from .constants import EntityType, BookingStatus, DateFilters

# libraries for generating pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
# library for generating excel
import xlwt
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsUserOwner, IsBookingOwner


# Create your views here.

# load dynamic images in pdf
# def fetch_resources(uri, rel):
#     path = os.path.join(uri.replace(settings.STATIC_URL, ""))
#     return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)  # , link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_total_bookings_of_product(product_id, start_time, end_time, is_cancelled=False):
    bookings_count = BookedProducts.objects.select_related('booking') \
        .filter(product_id=product_id, is_cancelled=is_cancelled) \
        .filter(
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gt=start_time)) |
        Q(Q(booking__start_time__lt=end_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__gte=start_time) & Q(booking__end_time__lte=end_time))
    ).aggregate(sum=Sum('quantity'))['sum']
    if bookings_count is None:
        return 0
    return bookings_count


def valid_booking(products_list, start_time, end_time):
    now = datetime.now()
    if now.strftime(get_date_format()) >= start_time:
        return "Start time is greater than persent time", ""
    if start_time >= end_time:
        return "end time is less than start time", ""
    for product in products_list:
        if product['quantity'] <= 0:
            return "quantity is less than 0 ", product['product_id']
        previous_bookings = get_total_bookings_of_product(product['product_id'], start_time, end_time)
        total_quantity = getTotalQuantityOfProduct(product['product_id'])
        if total_quantity - previous_bookings < product['quantity']:
            if total_quantity - previous_bookings == 0:
                return "Sorry, No products are available", product['product_id']
            return "Sorry, only {} products are available".format(total_quantity - previous_bookings), product[
                'product_id']
    return "", ""


def cancelProductStatus(booking_id):
    booked_products = BookedProducts.objects.select_related('booking').filter(booking=booking_id) \
        .filter(~Q(product_status=BookingStatus.cancelled.value))
    booked_products.update(is_cancelled=True, product_status=BookingStatus.cancelled.value)
    return True


def getBookingDetails(booking_ids):
    return Bookings.objects.filter(booking_id__in=booking_ids)


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status


def changeBookingStatus(booking_id, status):
    return Bookings.objects.filter(booking_id=booking_id).update(booking_status=status)


def dateFilters(request):
    date_filters = [date_filter.value for date_filter in DateFilters]
    return HttpResponse([date_filters], 200)


class CreateBooking(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user
        new_booking_serializer = NewBookingSerializer(data=request.data)
        if new_booking_serializer.is_valid():
            products_list = request.data.pop('products', None)
            comment, product_id = valid_booking(products_list, request.data['start_time'], request.data['end_time'])
            if len(comment) == 0:
                product_ids = []
                entity_id = request.data['entity_id']
                for product in products_list:
                    product_ids.append(product['product_id'])
                product_values = getIndividualProductValue(product_ids)
                total_money = 0.0
                for product in products_list:
                    total_money += product_values[product['product_id']]['price'] * product['quantity']
                is_valid, copoun_reducted_money = getCouponValue(request.data['coupon'], product_ids, entity_id,
                                                                 total_money)
                if is_valid is False:
                    return Response({"message": "Coupon is invalid"}, 400)
                request.data['total_money'] = total_money - copoun_reducted_money
                payment_status = request.data.pop('payment_status')
                bookings_object = BookingsSerializer()
                booking_id = (bookings_object.create(request.data))
                for product in products_list:
                    product['booking'] = booking_id
                    product["product_value"] = product_values[product['product_id']]['price']
                booked_product_serializer_object = BookedProductsSerializer()
                booked_product_serializer_object.bulk_create(products_list)
                create_transaction = createTransaction(str(booking_id), request.data['entity_id'], \
                                    request.data['entity_type'], request.data['total_money'], payment_status, \
                                    booking_id.booking_date)
                return Response("Success", 200)
            else:
                return Response({product_id + " " + comment}, 400)
        else:
            return Response(new_booking_serializer.errors, 400)


class UserBookingsList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        self.queryset = Bookings.objects.filter(user=user)
        return super().get(request, *args, **kwargs)


class CancelBookingView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)
    serializer_class = BookingsSerializer
    # check booking whether users or not.

    def put(self, request, *args, **kwargs):
        input_serializer = CancelBookingSerializer(data=request.data)
        if input_serializer.is_valid():
            booking = Bookings.objects.filter(booking_id=request.data['booking_id'])
            if len(booking) == 0:
                return Response({"message": "Booking does'nt exist"}, 400)
            self.check_object_permissions(request,booking[0])
            cancelled_serializer = CancelledDetailsSerializer()
            cancelled_serializer.create(booking[0])
            cancelProductStatus(request.data['booking_id'])
            booking.update(booking_status=BookingStatus.cancelled.value)
            return Response({"message": "success"},200)
        else:
            return Response(input_serializer.errors, 400)


class BookingsStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,)
# check entity by business client
    def get(self, request, *args, **kwargs):
        input_serializer = StatisticsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            entity_id = request.data['entity_id']
            if date_filter == 'Total':
                received_bookings = Bookings.objects.total_received_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                ongoing_bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                pending_bookings = Bookings.objects.pending_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                cancelled_bookings = Bookings.objects.total_cancelled_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                customer_take_aways_bookings = Bookings.objects.total_customer_yet_to_take_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                return_bookings = Bookings.objects.total_return_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                customer_taken_bookings = CheckInDetails.objects.total_customer_taken_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                returned_bookings = CheckOutDetails.objects.total_returned_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                return HttpResponse([{"received": received_bookings,
                                     "ongoing": ongoing_bookings,
                                     "pending": pending_bookings,
                                     "cancelled": cancelled_bookings,
                                     "customer_yet_to_take": customer_take_aways_bookings,
                                     "yet_to_return": return_bookings,
                                     "cutomer_taken": customer_taken_bookings,
                                     "returned": returned_bookings}], 200)
            elif date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
                received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                cancelled_bookings = CancelledDetails.objects \
                        .cancelled_bookings(from_date, to_date, entity_filter, entity_id) \
                        .aggregate(count=Count('booking_id'))['count']
                customer_taken_bookings = CheckInDetails.objects \
                        .customer_taken(from_date, to_date, entity_filter, entity_id) \
                        .aggregate(count=Count('booking_id'))['count']
                returned_bookings = CheckOutDetails.objects \
                        .returned_bookings(from_date, to_date, entity_filter, entity_id) \
                        .aggregate(count=Count('booking_id'))['count']
                return HttpResponse([{"received": received_bookings,
                                     "ongoing ": -1,
                                     "pending": -1,
                                     "cancelled": cancelled_bookings,
                                     "customer_taken": customer_taken_bookings,
                                     "returned": returned_bookings}], 200)
            else:
                from_date, to_date = getTimePeriod(date_filter)
                previous_from_date, previous_to_date = getPreviousTimePeriod(date_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id) \
                .aggregate(count=Count('booking_id'))['count']
            if date_filter == 'Today':
                ongoing_bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                pending_bookings = Bookings.objects.pending_bookings(entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
            else:
                ongoing_bookings = pending_bookings = -1
            cancelled_bookings = CancelledDetails.objects \
                    .cancelled_bookings(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
            if date_filter != 'Yesterday':
                customer_take_aways_bookings = Bookings.objects \
                    .customer_yet_to_take_bookings(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                return_bookings = Bookings.objects \
                    .yet_to_return_bookings(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                customer_taken_bookings = CheckInDetails.objects \
                    .customer_taken(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
                returned_bookings = CheckOutDetails.objects \
                    .returned_bookings(from_date, to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']

            else:
                customer_take_aways_bookings = return_bookings = customer_taken_bookings = returned_bookings = -1
            previous_receiving_bookings = Bookings.objects \
                    .received_bookings(previous_from_date, previous_to_date, entity_filter, entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
            previous_cancelled_bookings = CancelledDetails.objects \
                    .cancelled_bookings(previous_from_date, previous_to_date, entity_filter,entity_id) \
                    .aggregate(count=Count('booking_id'))['count']
            return HttpResponse([{"received": received_bookings,
                                "percentage_change": (received_bookings - previous_receiving_bookings) / 100},
                                {"ongoing": ongoing_bookings},
                                {"pending": pending_bookings},
                                {"cancelled": cancelled_bookings,
                                "percentage_change": (cancelled_bookings - previous_cancelled_bookings) / 100},
                                {"customer_yet_to_take": customer_take_aways_bookings},
                                {"yet_to_return": return_bookings},
                                {'customer_taken' : customer_taken_bookings},
                                {'returned' : returned_bookings}], 200)
        else:
            return Response(input_serializer.errors, 400)


class GetBookingsStatisticsDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,)
# same as upper
    def get(self, request, *args, **kwargs):
        input_serializer = GetBookingsStatisticsDetailsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            entity_id = request.data['entity_id']
            statistics_details_type = request.data['statistics_details_type']
            if date_filter == 'Total':
                if statistics_details_type == 'received_bookings':
                    bookings = Bookings.objects.total_received_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'ongoing_bookings':
                    bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'pending_bookings':
                    bookings = Bookings.objects.pending_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'cancelled_bookings':
                    bookings = Bookings.objects.total_cancelled_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'customer_take_aways':
                    bookings = Bookings.objects.total_customer_yet_to_take_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'return_bookings':
                    bookings = Bookings.objects.total_return_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'customer_taken_bookings':
                    bookings = CheckInDetails.objects.total_customer_taken_bookings(entity_filter, entity_id)
                elif statistics_details_type == 'returned_bookings':
                    bookings = CheckOutDetails.objects.total_returned_bookings(entity_filter, entity_id)
                serializer = StatisticsDetailsSerializer(bookings, many=True)
                return Response(serializer.data, 200)

            elif date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            else:
                bookings = []
                if date_filter == 'Today':
                    if statistics_details_type == 'ongoing_bookings':
                        bookings = Bookings.objects.ongoing_bookings(entity_filter, entity_id)
                    elif statistics_details_type == 'pending_bookings':
                        bookings = Bookings.objects.pending_bookings(entity_filter, entity_id)
                if statistics_details_type == 'customer_take_aways':
                    bookings = Bookings.objects.customer_yet_to_take_bookings(from_date, to_date, entity_filter, entity_id)
                elif statistics_details_type == 'return_bookings':
                    bookings = Bookings.objects.yet_to_return_bookings(from_date, to_date, entity_filter, entity_id)
                elif statistics_details_type == 'customer_taken':
                    customer_taken_bookings = CheckInDetails.objects \
                        .customer_taken(from_date, to_date, entity_filter, entity_id)
                    booking_ids = []
                    for each_customer in customer_taken_bookings:
                        booking_ids.append(each_customer.booking_id)
                    bookings = getBookingDetails(booking_ids)
                elif statistics_details_type == 'returned_bookings':
                    returned_bookings = CheckOutDetails.objects \
                        .returned_bookings(from_date, to_date, entity_filter, entity_id)
                    booking_ids = []
                    for each_returned_booking in returned_bookings:
                        booking_ids.append(each_returned_booking.booking_id)
                    bookings = getBookingDetails(booking_ids)
                elif statistics_details_type == 'received_bookings':
                    bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
                elif statistics_details_type == 'cancelled_bookings':
                    cancelled_bookings = CancelledDetails.objects \
                        .cancelled_bookings(from_date, to_date, entity_filter, entity_id)
                    booking_ids = []
                    for each_cancelled_booking in cancelled_bookings:
                        booking_ids.append(each_cancelled_booking.booking_id)
                    bookings = getBookingDetails(booking_ids)
                serializer = StatisticsDetailsSerializer(bookings, many=True)
                return Response(serializer.data, 200)

        else:
            return Response(input_serializer.errors, 400)


class CancelProductStatusView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)
    serializer_class = BookedProductsSerializer

    def put(self, request, *args, **kwargs):
        input_serializer = CancelProductStatusSerializer(data=request.data)
        if input_serializer.is_valid():
            booking_product = BookedProducts.objects \
                    .filter(booking=request.data['booking_id'], product_id=request.data['product_id'])
            if len(booking_product) == 0:
                return Response({"Invalid Booking id {} or product  {} " \
                                .format(request.data['booking_id'], request.data['product_id'])}, 400)
            booking = Bookings.objects.get(booking_id=request.data['booking_id'])
            self.check_object_permissions(request,booking)
            booking_product.update(is_cancelled=True,product_status = BookingStatus.cancelled.value)
            return Response({"Booking_status":" Changed successfully"})
        else:
            return Response(input_serializer.errors, 400)


class GetSpecificBookingDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.select_related('user').get(booking_id=kwargs['booking_id'])
        except:
            return Response({"message: invalid booking id in url"}, 400)
        booking = Bookings.objects.get(booking_id=kwargs['booking_id'])
        self.check_object_permissions(request,booking)
        user_data = Bookings.objects.none()
        user_data.name = booking.user.first_name + booking.user.last_name
        user_data.contact_number = booking.user.phone_number
        user_data.email = booking.user
        booking.User_Details = user_data
        all_products = BookedProducts.objects.filter(booking=booking)
        products = []
        for product in all_products:
            some_data_product = BookedProducts.objects.none()
            some_data_product.product_id = product.product_id
            some_data_product.quantity = product.quantity
            products.append(some_data_product)
        booking.products = products
        serializer = GetSpecificBookingDetailsSerializer(booking).data
        serializer['transaction_details'] = getTransactionDetailsByBookingId(booking.booking_id)
        serializer['customer_review'] = getReviewByBookingId(booking.booking_id)
        return Response(serializer, 200)


class GetBookingDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient)

    def get(self, request, *args, **kwargs):
        input_serializer = GetBookingDetailsViewSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            category_filter = getCategoryFilter(request.data['category_filter'])
            status_filter = getStatus(request.data['status_filter'])
            entity_id = request.data['entity_id']
            from_date, to_date = getTimePeriod(date_filter)
            booking_details = Bookings.objects \
                .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                          & Q(entity_type__in=category_filter) & Q(booking_status__in=status_filter) \
                          & Q(entity_id__in=entity_id)))
            booked_product_details = BookedProducts.objects.select_related('booking') \
                .filter(Q(Q(booking__booking_date__gte=from_date) & Q(booking__booking_date__lte=to_date) \
                          & Q(booking__entity_type__in=category_filter) & Q(booking__booking_status__in=status_filter) \
                          & Q(booking__entity_id__in=entity_id)))
            booking_check_in = CheckInDetails.objects.select_related('booking') \
                .filter(Q(Q(booking__booking_date__gte=from_date) & Q(booking__booking_date__lte=to_date) \
                          & Q(booking__entity_type__in=category_filter) & Q(booking__booking_status__in=status_filter) \
                          & Q(booking__entity_id__in=entity_id)))

            booking_check_out = CheckOutDetails.objects.select_related('booking') \
                .filter(Q(Q(booking__booking_date__gte=from_date) & Q(booking__booking_date__lte=to_date) \
                          & Q(booking__entity_type__in=category_filter) & Q(booking__booking_status__in=status_filter) \
                          & Q(booking__entity_id__in=entity_id)))
            product_ids = []
            for each_booked_product in booked_product_details:
                if each_booked_product.product_id not in product_ids:
                    product_ids.append(each_booked_product.product_id)
            product_details = getProductsDetails(product_ids)
            check_in_details = {}
            for each_check_in in booking_check_in:
                check_in_details[each_check_in.booking_id] = each_check_in
            check_out_details = {}
            for each_check_out in booking_check_out:
                check_out_details[each_check_out.booking_id] = each_check_out
            all_bookings_in_each_entity = []
            for each_booking in booking_details:
                each_booking_object = {}
                each_booking_object['booking_id'] = each_booking.booking_id
                each_booking_object['entity_type'] = each_booking.entity_type
                each_booking_object['booked_at'] = each_booking.booking_date
                days, minutes = (datetime.now() - each_booking.booking_date, "%d")
                days = str(days).split()[0]
                each_booking_object['ago'] = days + " days"
                check_in_flag = True
                try:
                    each_booking_object['check_in'] = check_in_details[str(each_booking.booking_id)].check_in
                except:
                    each_booking_object['check_in'] = "Still Booking Status is in Pending"
                    each_booking_object['check_out'] = "Still Booking Status is in Pending"
                    check_in_flag = False
                if check_in_flag:
                    try:
                        each_booking_object['check_out'] = check_out_details[str(each_booking.booking_id)].check_out
                    except:
                        each_booking_object['check_out'] = "Still Booking Status is in Ongoing"
                all_products = []
                for each_product in booked_product_details:
                    each_product_object = {'product_name': product_details[each_product.product_id]['name'],
                                           'product_type': product_details[each_product.product_id]['type']}
                    all_products.append(each_product_object)
                each_booking_object['products'] = all_products
                all_bookings_in_each_entity.append(each_booking_object)
            return Response(all_bookings_in_each_entity, 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingStart(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)

    def post(self, request, *args, **kwargs):
        booking = Bookings.objects.get(booking_id=request.data['booking_id'])
        self.check_object_permissions(request,booking)
        input_serializer = BookingStartSerializer(data=request.data)
        if input_serializer.is_valid():
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
            change_booking_status = changeBookingStatus(data['booking_id'], BookingStatus.ongoing.value)
            return Response("success", 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingEnd(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)

    def post(self, request, *args, **kwargs):
        booking = Bookings.objects.get(booking_id=request.data['booking_id'])
        self.check_object_permissions(request,booking)
        input_serializer = BookingEndSerializer(data=request.data)
        if input_serializer.is_valid():
            data = request.data.dict()
            other_images = request.data.pop('product_images', None)
            data.pop('product_images', None)
            review = data.pop('review', None)
            rating = data.pop('rating', None)
            booking_id = request.data['booking_id']
            user = request.user
            businessClientReviewOnCustomer(review, rating, booking_id, user)
            serializer = CheckOutDetailsSerializer()
            check_out = serializer.create(data)
            images = []
            for each_image in other_images:
                all_product_images = {'check_out': check_out, 'image': each_image}
                images.append(all_product_images)
            product_image_serializer = CheckOutImagesSerializer()
            product_image_serializer.bulk_create(images)
            change_booking_status = changeBookingStatus(data['booking_id'], BookingStatus.done.value)
            return Response("success", 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingEndBookingIdDetialsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)

    def get(self, request, *args, **kwargs):
        booking = Bookings.objects.get(booking_id=kwargs['booking_id'])
        self.check_object_permissions(request,booking)
        try:
            check_in_object = CheckInDetails.objects.get(booking_id=kwargs['booking_id'])
        except:
            return Response({"message": "since product is not completed, you cannot get access"}, 400)
        output = {}
        if check_in_object.is_caution_deposit_collected:
            output['is_caution_deposit_collected'] = True
            output['caution_amount'] = check_in_object.caution_amount
        else:
            output['is_caution_deposit_collected'] = False
        other_images = []
        other_image_ids = CheckInImages.objects.filter(check_in_id=check_in_object.id)
        for each_product_image_id in other_image_ids:
            other_images.append(str(each_product_image_id.image))
        output['other_images'] = other_images
        return Response(output, 200)


class ReportCustomerForBooking(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsBookingOwner)

    def post(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(booking_id=request.data['booking_id'])
        except:
            return Response({"message:": "Invalid booking id"}, 400)
        self.check_object_permissions(request,booking)
        request.data['booking'] = booking
        report_customer = ReportCustomerForBooking()
        report_customer.create(request.data)
        return Response("success", 200)


class GeneratePDF(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.all()
        except:
            return HttpResponse("505 Not Found")
        all_data = {}
        all_data['total_length'] = len(booking)
        count = 0
        data1 = []
        for each_booking in booking:
            data = {
                'booking_id': each_booking.booking_id,
                'booking_date': each_booking.booking_date,
                'booking_status': each_booking.booking_status,
            }
            count += 1
            data1.append(data)
        all_data['data'] = data1
        pdf = render_to_pdf('pdf.html', all_data)
        # return HttpResponse(pdf, content_type='application/pdf')

        # force download
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "bookings%s.pdf" % (data['booking_id'])
            content = "inline; filename='%s'" % (filename)
            # download = request.GET.get("download")
            # if download:
            content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


def generate_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=excelexample' + \
                                      str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    coloumns = ['Booking Id', 'Booking Date', 'Booking Status']
    for col_num in range(len(coloumns)):
        ws.write(row_num, col_num, coloumns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Bookings.objects.all().values_list('booking_id', 'booking_date', 'booking_status')

    for row in rows:
        row_num += 1

        for col_num in range(3):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


class GetBookingDetailsOfProductId(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, )

    def get(self, request, *args, **kwargs):
        all_booked_products = BookedProducts.objects.all()
        booked_product_dict = {}
        for each_booked_product in all_booked_products:
            each_product = {'product_id': each_booked_product.product_id, 'quantity': each_booked_product.quantity,
                            'product_value': each_booked_product.product_value,
                            'product_status': each_booked_product.product_status}
            booked_product_dict[str(each_booked_product.booking_id)] = booked_product_dict.get(
                str(each_booked_product.booking_id), []) + [each_product]
        get_bookings_details_of_product = []
        bookings_of_particular_product = BookedProducts.objects.select_related('booking') \
            .filter(product_id=kwargs['product_id'])
        booking_check_in_details = CheckInDetails.objects.all()
        check_in_details = {}
        for each_check_in in booking_check_in_details:
            check_in_details[each_check_in.booking_id] = each_check_in
        booking_check_out_details = CheckOutDetails.objects.all()
        check_out_details = {}
        for each_check_out in booking_check_out_details:
            check_out_details[each_check_out.booking_id] = each_check_out
        for each_booking_of_particular_product in bookings_of_particular_product:
            each_booking_details = {'booking_id': str(each_booking_of_particular_product.booking_id),
                                    'booking_date': each_booking_of_particular_product.booking.booking_date,
                                    'entity_id': each_booking_of_particular_product.booking.entity_id,
                                    'start_time': each_booking_of_particular_product.booking.start_time,
                                    'end_time': each_booking_of_particular_product.booking.end_time,
                                    'entity_type': each_booking_of_particular_product.booking.entity_type}
            check_out_flag = True
            try:
                each_booking_details['check_in'] = check_in_details[
                    str(each_booking_of_particular_product.booking_id)].check_in
            except:
                each_booking_details['check_in'] = "Still Booking Status is in Pending"
                each_booking_details['check_out'] = "Still Booking Status is in Pending"
                check_out_flag = False
            if check_out_flag:
                try:
                    each_booking_details['check_out'] = check_out_details[
                        each_booking_of_particular_product.booking_id].check_out
                except:
                    each_booking_details['check_out'] = "Still Booking Status is in Pending"
            each_booking_details['products'] = booked_product_dict[str(each_booking_of_particular_product.booking)]
            get_bookings_details_of_product.append(each_booking_details)
        return Response(get_bookings_details_of_product, 200)


class ReportCustomerResonsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee, )
    queryset = ReportCustomerResons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class ReportCustomerResonsDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient)
    queryset = ReportCustomerResons.objects.all()
    serializer_class = ReportCustomerResonsSerializer


class ProductStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = ProductStatisticsSerializer(data=request.data)
        if input_serializer.is_valid():
            date = datetime.strptime(request.data['date'],"%Y-%m-%d")
            tomorrow_date = date + timedelta(1)
            product_id = kwargs['product_id']
            total_products = getTotalQuantityOfProduct(product_id)
            total_products_booked = BookedProducts.objects.select_related('booking') \
                    .filter(product_id=product_id,booking__booking_date__gte=date, \
                    booking__booking_date__lte=tomorrow_date).aggregate(count=Sum(F('quantity')))['count']
            total_products_cancelled = BookedProducts.objects.select_related('booking') \
                    .filter(product_id=product_id,booking__booking_date__gte=date, \
                    booking__booking_date__lte=tomorrow_date, is_cancelled=True) \
                    .aggregate(count=Sum(F('quantity')))['count']
            if total_products_cancelled is None:
                total_products_cancelled = 0
            if total_products_booked is None:
                total_products_booked = 0
            remaining_products = total_products - total_products_booked + total_products_cancelled
            ongoing_products = BookedProducts.objects.select_related('booking') \
                .filter(product_id=product_id,booking__booking_date__gte=date, \
                booking__booking_date__lte=tomorrow_date, \
                booking__booking_status=BookingStatus.ongoing.value).aggregate(count=Sum(F('quantity')))['count']
            if ongoing_products is None:
                ongoing_products = 0
            return Response({"total_products_booked" : total_products_booked,
                             "total_products_cancelled" : total_products_cancelled,
                             "remaining_products" : remaining_products,
                             "ongoing_products" : ongoing_products},200)
        else:
            return Response(input_serializer.errors, 400)