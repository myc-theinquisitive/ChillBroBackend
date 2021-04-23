from django.db.models import Q, F, FloatField
from django.utils.datetime_safe import strftime
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from Payments.models import *
from ReviewsRatings.models import ReviewsRatings
from .serializers import *
from .wrapper import getIndividualProductValue, getCouponValue, getTotalQuantityOfProduct, businessClientReviewOnCustomer \
        , getTransactionDetailsByBookingId, getTransactionDetails
from datetime import timedelta, date, datetime
from .helpers import getTodayDate, getTodayDay, get_date_format
from .constants import EntityType, BookingStatus, DateFilters
from django.db.models import Sum

# libraries for generating pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
# library for generating excel
import xlwt


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
    return BookedProducts.objects.select_related('booking') \
        .filter(product_id=product_id, is_cancelled=is_cancelled) \
        .filter(
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gt=start_time)) |
        Q(Q(booking__start_time__lt=end_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__gte=start_time) & Q(booking__end_time__lte=end_time))
    ).aggregate(sum=Sum('quantity'))['sum']


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
        if previous_bookings is None:
            previous_bookings = 0
        total_quantity = getTotalQuantityOfProduct(product['product_id'])
        if total_quantity - previous_bookings < product['quantity']:
            if total_quantity - previous_bookings == 0:
                return "Sorry, No products are available", product['product_id']
            return "Sorry, only {} products are available".format(total_quantity - previous_bookings), product[
                'product_id']
    return "", ""


def UpdateProductStatus(booking_id):
    booked_products = BookedProducts.objects.select_related('booking').filter(booking=booking_id) \
        .filter(~Q(product_status=BookingStatus.cancelled.value))
    booked_products.update(is_cancelled=True, product_status=BookingStatus.cancelled.value)
    return True


def CalculateStatisticsValues(total_bookings):
    ongoing_bookings = pending_bookings = cancelled_bookings = customer_take_aways = return_bookings = 0
    today_date = datetime.now()
    for booked_product in total_bookings:
        if booked_product.booking_status == BookingStatus.pending.value and booked_product.start_time <= today_date:
            customer_take_aways += 1
        elif booked_product.booking_status == BookingStatus.ongoing.value and booked_product.end_time <= today_date:
            return_bookings += 1
        elif booked_product.booking_status == BookingStatus.ongoing.value:
            ongoing_bookings += 1
        elif booked_product.booking_status == BookingStatus.pending.value:
            pending_bookings += 1
        elif booked_product.booking_status == BookingStatus.cancelled.value:
            cancelled_bookings += 1


    return ongoing_bookings, pending_bookings, cancelled_bookings, customer_take_aways, return_bookings


def getEntityType(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities


def getCategoryFilter(category_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(category_filter) == 1 and category_filter[0] == 'ALL':
        return entities
    return category_filter


def getTimePeriod(date_filter):
    if date_filter == 'Today':
        today = date.today()
        tomorrow = today + timedelta(1)
        return today, tomorrow
    elif date_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        return week, today + timedelta(1)
    elif date_filter == 'Month':
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, today + timedelta(1)
    return None, None


def getPreviousTimePeriod(date_filter):
    if date_filter == 'Today':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        day_before_yesterday = today - timedelta(2)
        return day_before_yesterday, yesterday
    elif date_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        previous_week = week - timedelta(7)
        return previous_week, week
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(getTodayDate())
        previous_month = month - timedelta(days_in_months[today.month]+1)
        return previous_month, month


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status


def getPaymentStatus(payment_status):
    if len(payment_status) == 0:
        return [payment_status.value for payment_status in PayStatus]
    return payment_status


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
                bookings_object = BookingsSerializer()
                bookings_id = (bookings_object.create(request.data))
                for product in products_list:
                    product['booking'] = bookings_id
                    product["product_value"] = product_values[product['product_id']]['price']
                booked_product_serializer_object = BookedProductsSerializer()
                booked_product_serializer_object.bulk_create(products_list)
                return Response("Success", 200)
            else:
                return Response({product_id + " " + comment}, 400)
        else:
            return Response(new_booking_serializer.errors, 400)


class BookedProductsList(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = BookingIdSerializer(data=request.data)
        if input_serializer.is_valid():
            product_status = getStatus(request.data['product_status'])
            booked_products = BookedProducts.objects.filter(booking=request.data['booking_id'],
                                                            product_status__in=product_status)
            if len(booked_products) == 0:
                return Response({"message": "Booking does'nt exist"}, 400)
            serialize = BookedProductsSerializer(booked_products, many=True)
            return Response(serialize.data, 200)
        else:
            return Response(input_serializer.errors, 400)


class UserBookingsList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        self.queryset = Bookings.objects.filter(user=user)
        return super().get(request, *args, **kwargs)


class CancelBookingView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookingsSerializer

    def put(self, request, *args, **kwargs):
        input_serializer = CancelBookingSerializer(data=request.data)
        if input_serializer.is_valid():
            try:
                booking = Bookings.objects.get(booking_id=request.data['booking_id'])
            except:
                return Response({"message": "Booking does'nt exist"}, 400)
            cancelled_serializer = CancelledDetailsSerializer()
            cancelled_serializer.create(booking)
            UpdateProductStatus(request.data['booking_id'])
            request.data['user'] = request.user.id
            request.data['coupon'] = booking.coupon
            request.data['booking_status'] = BookingStatus.cancelled.value
            request.data['entity_id'] = booking.entity_id
            request.data['start_time'] = booking.start_time
            request.data['end_time'] = booking.end_time
            serializer = self.serializer_class(booking, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, 200)
            else:
                return Response(serializer.errors, 400)
        else:
            return Response(input_serializer.errors, 400)


class BookedDetailsListFilter(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = BookingsDetailsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            status = getStatus(request.data['status'])
            payment_status = getPaymentStatus(request.data['payment_status'])
            from_date, to_date = getTimePeriod(date_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            elif entity_filter is None:
                return Response({"message": "Invalid Entity Filter!!!"}, 400)
            else:
                bookings = Bookings.objects \
                    .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                              & Q(entity_type__in=entity_filter) & Q(booking_status__in=status) \
                              & Q(payment_status__in=payment_status)))
            serializer = BookingsSerializer(bookings, many=True)
            return Response(serializer.data, 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingsStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = StatisticsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            entity_id = request.data['entity_id']
            if date_filter == 'Total':
                received_bookings = Bookings.objects.total_received_bookings(entity_filter, entity_id)
                ongoing_bookings = Bookings.objects.total_ongoing_bookings(entity_filter, entity_id)
                pending_bookings = Bookings.objects.total_pending_bookings(entity_filter, entity_id)
                cancelled_bookings = Bookings.objects.total_cancelled_bookings(entity_filter, entity_id)
                customer_take_aways_bookings = Bookings.objects.total_customer_take_aways_bookings(entity_filter, entity_id)
                return_bookings = Bookings.objects.total_return_bookings(entity_filter, entity_id)
                return HttpResponse([{"received : ": str(received_bookings)
                                         , "ongoing : ": str(ongoing_bookings)
                                         , "pending : ": str(pending_bookings)
                                         , "cancelled : ": str(cancelled_bookings)
                                         , "current take away : ": str(customer_take_aways_bookings)
                                         , "return bookings : ": str(return_bookings)}], 200)
            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
                received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
                ongoing_bookings = Bookings.objects.ongoing_bookings(from_date, to_date, entity_filter, entity_id)
                pending_bookings = Bookings.objects.pending_bookings(from_date, to_date, entity_filter, entity_id)
                cancelled_bookings = Bookings.objects.cancelled_bookings(from_date, to_date, entity_filter, entity_id)
                customer_take_aways_bookings = Bookings.objects.customer_take_aways_bookings(from_date, to_date,entity_filter, entity_id)
                return_bookings = Bookings.objects.return_bookings(from_date, to_date, entity_filter, entity_id)
                return HttpResponse([{"received : " : str(received_bookings)
                                        , "ongoing : " : str(ongoing_bookings)
                                        , "pending : " : str(pending_bookings)
                                        , "cancelled : " : str(cancelled_bookings)
                                        , "current take away : " : str(customer_take_aways_bookings)
                                        , "return bookings : " : str(return_bookings)}], 200)
            else:
                from_date, to_date = getTimePeriod(date_filter)
                previous_from_date, previous_to_date = getPreviousTimePeriod(date_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            received_bookings = Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
            ongoing_bookings = Bookings.objects.ongoing_bookings(from_date, to_date, entity_filter, entity_id)
            pending_bookings = Bookings.objects.pending_bookings(from_date, to_date, entity_filter, entity_id)
            cancelled_bookings = Bookings.objects.cancelled_bookings(from_date, to_date, entity_filter, entity_id)
            customer_take_aways_bookings = Bookings.objects.customer_take_aways_bookings(from_date, to_date, entity_filter, entity_id)
            return_bookings = Bookings.objects.return_bookings(from_date, to_date, entity_filter, entity_id)
            previous_receiving_bookings = Bookings.objects.return_bookings(previous_from_date, previous_to_date, entity_filter, entity_id)
            previous_cancelled_bookings = Bookings.objects.return_bookings(previous_from_date, previous_to_date, entity_filter, entity_id)
            return HttpResponse([{"Total": str(received_bookings),"percentage_change": str((received_bookings - previous_receiving_bookings) / 100)}
                                , {"ongoing": str(ongoing_bookings)}
                                , {"pending": str(pending_bookings)}
                                , {"cancelled": str(cancelled_bookings),
                                   "percentage_change": str((cancelled_bookings - previous_cancelled_bookings) / 100)}
                                , {"current_take_away": str(customer_take_aways_bookings)}
                                , {"return_bookings": str(return_bookings)}], 200)
        else:
            return Response(input_serializer.errors, 400)


class GetBookingsStatisticsDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = GetBookingsStatisticsDetailsSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            entity_id = request.data['entity_id']
            statistics_details_type = request.data['statistics_details_type']
            if date_filter == 'Total':
                if statistics_details_type == 'received_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'ongoing_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'pending_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'cancelled_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'customer_take_aways':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'return_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                serializer = ShowStatisticsDetailsSerializer(bookings, many=True)
                return Response(serializer.data, 200)

            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            else:
                if statistics_details_type == 'received_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'ongoing_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'pending_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'cancelled_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'customer_take_aways':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                elif statistics_details_type == 'return_bookings':
                    bookings = Bookings.objects.select_related('user') \
                        .filter(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id))
                serializer = ShowStatisticsDetailsSerializer(bookings, many=True)
                return Response(serializer.data, 200)

        else:
            return Response(input_serializer.errors, 400)


class CancelProductStatusView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookedProductsSerializer

    def put(self, request, *args, **kwargs):
        input_serializer = CancelProductStatusSerializer(data=request.data)
        if input_serializer.is_valid():
            try:
                booking_product = BookedProducts.objects \
                    .get(booking=request.data['booking_id'], product_id=request.data['product_id'])
            except:
                return Response({"Invalid Booking id {} or product  {} " \
                                .format(request.data['booking_id'], request.data['product_id'])}, 400)
            request.data['quantity'] = booking_product.quantity
            request.data['booking'] = request.data.pop('booking_id')
            serializer = self.serializer_class(booking_product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, 200)
            else:
                return Response(serializer.errors, 400)
        else:
            return Response(input_serializer.errors, 400)


class PaymentRevenueStatisticsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = PaymentRevenueStatisticsViewSerializer(data=request.data)
        if input_serializer.is_valid():
            date_filter = request.data['date_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            entity_id = request.data['entity_id']
            if date_filter == 'Total':
                total_revenue = Bookings.objects \
                    .filter(Q(entity_id__in=entity_id) & Q(entity_type__in=entity_filter)) \
                    .aggregate(total_value=Sum(F('total_money'), output_field=FloatField()))
                return Response(total_revenue['total_value'],200)
            if date_filter == 'Custom':
                from_date, to_date = request.data['custom_dates']['from_date'], request.data['custom_dates']['to_date']
            else:
                from_date, to_date = getTimePeriod(date_filter)
            bookings_on_date_filter = Bookings.objects \
                .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                          & Q(entity_type__in=entity_filter) & Q(entity_id__in=entity_id)))
            total_bookings = Bookings.objects \
                .filter(Q(Q(entity_id__in=entity_id) & Q(entity_type__in=entity_filter)))
            received_amount_date_filter_value, pending_amount_date_filter_value, total_received_amount_value, total_pending_amount_value = 0, 0, 0, 0
            for each_booking in bookings_on_date_filter:
                if each_booking.payment_status == PayStatus.done.value:
                    received_amount_date_filter_value += each_booking.total_money
                elif each_booking.payment_status == PayStatus.pending.value:
                    pending_amount_date_filter_value += each_booking.total_money
            for total_booking in total_bookings:
                if total_booking.payment_status == PayStatus.done.value:
                    total_received_amount_value += total_booking.total_money
                elif total_booking.payment_status == PayStatus.pending.value:
                    total_pending_amount_value += total_booking.total_money
            return Response([{
                "recieved_amount": {
                    "today": received_amount_date_filter_value + pending_amount_date_filter_value,
                    "total": total_received_amount_value + total_pending_amount_value
                }}, {
                "generated_revenue": {
                    "today": received_amount_date_filter_value,
                    "total": total_received_amount_value
                }}, {
                "pending_amount": {
                    "today": pending_amount_date_filter_value,
                    "total": total_pending_amount_value
                }}],200)
        else:
            return Response(input_serializer.errors, 400)


class GetSpecificBookingDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            booking_id = Bookings.objects.select_related('user').get(booking_id=kwargs['booking_id'])
        except:
            return Response({"message: invalid booking id in url"}, 400)
        user_data = Bookings.objects.none()
        user_data.name = booking_id.user.first_name + booking_id.user.last_name
        user_data.contact_number = booking_id.user.phone_number
        user_data.email = booking_id.user
        booking_id.User_Details = user_data
        all_products = BookedProducts.objects.filter(booking=booking_id)
        products = []
        for product in all_products:
            some_data_product = BookedProducts.objects.none()
            some_data_product.product_id = product.product_id
            some_data_product.quantity = product.quantity
            products.append(some_data_product)
        booking_id.products = products
        try:
            print("came")
            booking_id.transaction_details = getTransactionDetailsByBookingId(booking_id.booking_id)
        except:
            pass
        try:
            check_out_details = CheckOutDetails.objects.get(booking = booking_id)
            review_details = ReviewsRatings.objects.get(related_id = booking_id)
            booking_id.customer_review = review_details
        except:
            pass
        serializer = GetSpecificBookingDetailsSerializer(booking_id)
        return Response(serializer.data, 200)


class GetBookingDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

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
            product_details = BookedProducts.objects.select_related('booking') \
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

            all_bookings_in_each_entity = []
            for each_booking in booking_details:
                each_booking_object = {}
                each_booking_object['booking_id'] = each_booking.booking_id
                each_booking_object['entity_type'] = each_booking.entity_type
                each_booking_object['booked_at'] = each_booking.booking_date
                days, minutes = (datetime.now() - each_booking.booking_date, "%d")
                days = str(days).split()[0]
                each_booking_object['ago'] = days + " days"
                check_in_flag = False
                for each_check_in in booking_check_in:  # doubt-is there any possibility of reducing for loop
                    if each_check_in.booking_id_id == each_booking.booking_id:
                        each_booking_object['check_in'] = each_check_in.check_in
                        check_in_flag = True
                        break
                if check_in_flag is False:
                    each_booking_object['check_in'] = "Still Booking Status is in Pending"
                    each_booking_object['check_out'] = "Still Booking Status is in Pending"
                else:
                    check_out_Flag = False
                    for each_check_out in booking_check_out:
                        if each_check_out.booking_id_id == each_booking.booking_id:
                            each_booking_object['check_out'] = each_check_out.check_out
                            check_out_Flag = True
                            break
                    if check_out_Flag is False:
                        each_booking_object['check_out'] = "Still Booking Status is in Ongoing"
                all_products = []
                for each_product in product_details:
                    each_product_object = {}
                    if each_product.booking_id_id == each_booking.booking_id:
                        each_product_object['product_name'] = 'xyz'
                        each_product_object['product_type'] = 'type'
                        all_products.append(each_product_object)
                each_booking_object['products'] = all_products
                all_bookings_in_each_entity.append(each_booking_object)
            return Response(all_bookings_in_each_entity, 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingStart(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = BookingStartSerializer(data=request.data)
        if input_serializer.is_valid():
            data = request.data.dict()
            other_images = request.data.pop('other_images', None)
            data.pop('other_images', None)
            serializer = CheckInDetailsSerializer()
            check_in = serializer.create(data)
            images = []
            for each_image in other_images:
                all_other_images = {'check_in': check_in, 'image': each_image}
                images.append(all_other_images)
            other_image_serializer = CheckInImagesSerializer()
            other_image_serializer.bulk_create(images)
            booking = Bookings.objects.get(booking_id=data['booking_id'])
            booking.booking_status = BookingStatus.ongoing.value
            booking.save()
            return Response("success", 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingEnd(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
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
            booking = Bookings.objects.get(booking_id=data['booking_id'])
            booking.booking_status = BookingStatus.done.value
            booking.save()
            return Response("success", 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingEndBookingIdDetialsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            check_in_object = CheckInDetails.objects.get(booking_id=kwargs['booking_id'])
            check_out_object = CheckOutDetails.objects.get(booking_id=kwargs['booking_id'])
        except:
            return Response({"message": "since product is not completed, you cannot get access"}, 400)
        output = {}
        if check_in_object.is_caution_deposit_collected == True:
            output['is_caution_deposit_collected'] = True
            output['caution_amount'] = check_in_object.caution_amount - check_out_object.caution_deposit_deductions
        else:
            output['is_caution_deposit_collected'] = False
        product_images = []
        product_image_ids = CheckOutImages.objects.filter(check_out_id=check_out_object.id)
        for each_product_image_id in product_image_ids:
            product_images.append(str(each_product_image_id.image))
        output['product_images'] = product_images
        return Response(output, 200)


class ReviewsBookingsOnReportCustomerList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            booking = Bookings.objects.get(booking_id=request.data['booking_id'])
        except:
            return Response({"message:": "Invalid booking id"}, 400)
        request.data['booking'] = booking
        report_customer = BusinessClientReportOnCustomerSerializer()
        report_customer.create(request.data)
        return Response("success", 200)


class GetPaymentsDetailsOfEachEntityView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        date_filter = request.data['date_filter']
        entity_filter = getEntityType(request.data['category_filters'])
        status = getStatus(request.data['status_filters'])
        if date_filter == 'Custom':
            from_date, to_date = request.data['custom_dates']['from'], request.data['custom_dates']['to']
        else:
            from_date, to_date = getTimePeriod(date_filter)
        transactions= getTransactionDetails()
        bookings = Bookings.objects \
            .filter(Q(Q(entity_id=kwargs['entity_id']) \
                      & Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                      & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))
        if len(bookings) == 0:
            return Response({"message": "invalid entity id or no bookings"}, 400)
        all_bookings = []
        for each_transaction in transactions:
            for each_booking in bookings:
                if each_booking.booking_id == each_transaction.booking_id:
                    break
            each_booking_list = {'booking_id': str(each_transaction.booking_id),
                                 'type': each_booking.entity_type,
                                 'transaction_id': each_transaction.transaction_id, 'utr': each_transaction.utr,
                                 'mode': each_transaction.mode, 'transaction_made_on': each_transaction.transaction_date,
                                 'status': each_booking.booking_status
                                 }
            all_bookings.append(each_booking_list)
        all_details = {"Total Count": len(bookings), "results": all_bookings}
        return Response(all_details, 200)


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
    permission_classes = (IsAuthenticated,)

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
        booking_check_out_details = CheckOutDetails.objects.all()
        for each_booking_of_particular_product in bookings_of_particular_product:
            each_booking_details = {'booking_id': str(each_booking_of_particular_product.booking_id),
                                    'booking_date': each_booking_of_particular_product.booking.booking_date,
                                    'entity_id': each_booking_of_particular_product.booking.entity_id,
                                    'start_time': each_booking_of_particular_product.booking.start_time,
                                    'end_time': each_booking_of_particular_product.booking.end_time,
                                    'entity_type': each_booking_of_particular_product.booking.entity_type}
            check_in_flag = False
            for each_check_in in booking_check_in_details:  # doubt-is there any possibility of reducing for loop
                if each_check_in.booking_id == str(each_booking_of_particular_product.booking_id):
                    each_booking_details['check_in'] = each_check_in.check_in
                    check_in_flag = True
                    break
            if check_in_flag is False:
                each_booking_details['check_in'] = "Still Booking Status is in Pending"
                each_booking_details['check_out'] = "Still Booking Status is in Pending"
            else:
                check_out_Flag = False
                for each_check_out in booking_check_out_details:
                    if each_check_out.booking_id == str(each_booking_of_particular_product.booking):
                        each_booking_details['check_out'] = each_check_out.check_out
                        check_out_Flag = True
                        break
                if check_out_Flag is False:
                    each_booking_details['check_out'] = "Still Booking Status is in Ongoing"
            each_booking_details['products'] = booked_product_dict[str(each_booking_of_particular_product.booking)]
            get_bookings_details_of_product.append(each_booking_details)
        return Response(get_bookings_details_of_product, 200)
