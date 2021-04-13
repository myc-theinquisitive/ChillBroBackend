from django.db.models import Q
from rest_framework import generics
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import BookingsSerializer, BookedProductsSerializer, BookingIdSerializer, NewBookingSerializer,\
    StatisticsSerializer, OrderDetailsSerializer
from .wrapper import getIndividualProductValue, getCouponValue
from datetime import timedelta, date
from .helpers import getTodayDate, getTodayDay
from .constants import EntityType, BookingStatus


# Create your views here.
def get_bookings_of_product(product_id, start_time, end_time, is_cancelled=False, order_by='start_time'):
    # getting active booking on the same product with in the new booking timings
    return BookedProducts.objects \
        .filter(product_id=product_id, is_cancelled=is_cancelled) \
        .filter(
        Q(Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
        Q(Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
        Q(Q(start_time__lte=start_time) & Q(end_time__gte=end_time)) |
        Q(Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
    ).order_by(order_by)


def valid_booking(products_list):
    for product in products_list:
        if product["start_time"] >= product['end_time']:
            return "end time is less than start time", product['product_id']
        if product['quantity'] <= 0:
            return "quantity is less than 0 ", product['product_id']
        previous_bookings = get_bookings_of_product(product['product_id'], product['start_time'], product['end_time'])
        total_quantity = 10
        if total_quantity - len(previous_bookings) < product['quantity']:
            return "Sorry, only {} products are available".format(total_quantity - len(previous_bookings)), product['product_id']
    return "", ""


class OrdersList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def post(self, request, *args, **kwargs):
        request.data['user'] = request.user
        new_booking_serializer = NewBookingSerializer(data=request.data)
        if new_booking_serializer.is_valid():
            products_list = request.data.pop('products', None)
            comment, product_id = valid_booking(products_list)
            if len(comment) == 0:

                product_ids = []
                entity_ids = []
                for product in products_list:
                    product_ids.append(product['product_id'])
                    entity_ids.append(product['entity_id'])
                product_values = getIndividualProductValue(product_ids)
                total_money = 0.0
                for product in products_list:
                    total_money += product_values[product['product_id']]['price'] * product['quantity']
                is_valid, copoun_reducted_money = getCouponValue(request.data['coupon'], product_ids, entity_ids, total_money)
                if is_valid:
                    return Response({"message": "Coupon is invalid"}, 400)
                request.data['total_money'] = total_money - copoun_reducted_money
                bookings_object = BookingsSerializer()
                bookings_id = (bookings_object.create(request.data))
                for product in products_list:
                    product['booking_id'] = bookings_id
                    product["product_value"] = product_values[product['product_id']]['price']
                ordered_product_serializer_object = BookedProductsSerializer()
                ordered_product_serializer_object.bulk_create(products_list)
                return Response("Success", 200)
            else:
                return Response({product_id +" "+comment}, 400)
        else:
            return Response(new_booking_serializer.errors, 400)


class OrderedProductsList(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = BookingIdSerializer(data=request.data)
        if input_serializer.is_valid():
            booking_id = request.data['booking_id']

            booked_products = BookedProducts.objects.filter(booking_id=booking_id)
            if len(booked_products) == 0:
                return Response({"message": "Order does'nt exist"}, 400)
            serialize = BookedProductsSerializer(booked_products, many=True)
            return Response(serialize.data, 200)
        else:
            return Response(input_serializer.errors, 400)


class OrderDeleteList(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer


class UserOrdersList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Bookings.objects.all()
    serializer_class = BookingsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        self.queryset = Bookings.objects.filter(user=user)
        return super().get(request, *args, **kwargs)


class CancelOrderList(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookingsSerializer

    def put(self, request, *args, **kwargs):
        input_serializer = BookingIdSerializer(data=request.data)
        if input_serializer.is_valid():
            try:
                booking = Bookings.objects.get(booking_id=request.data['booking_id'])
            except:
                return Response({"message": "Order does'nt exist"}, 400)
            request.data['user'] = request.user.id
            request.data['coupon'] = booking.coupon
            request.data['booking_status'] = BookingStatus.cancelled.value
            serializer = self.serializer_class(booking, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, 200)
            else:
                return Response(serializer.errors, 400)
        else:
            return Response(input_serializer.errors, 400)


class OrderDetailsListFilter(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = OrderDetailsSerializer(data = request.data)
        if input_serializer.is_valid():
            booking_filter = request.data['booking_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            status = getStatus(request.data['status'])
            from_date, to_date = getTimePeriod(booking_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            elif entity_filter is None:
                return Response({"message": "Invalid Entity Filter!!!"}, 400)
            else:
                bookings = Bookings.objects \
                    .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                              & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))
            serializer = BookingsSerializer(bookings, many=True)
            return Response(serializer.data, 200)
        else:
            return Response(input_serializer.errors, 400)


class BookingsStatistics(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = StatisticsSerializer(data = request.data)
        if input_serializer.is_valid():
            booking_filter = request.data['booking_filter']
            entity_filter = getEntityType(request.data['entity_filter'])
            from_date, to_date = getTimePeriod(booking_filter)
            if from_date is None and to_date is None:
                return Response({"message": "Invalid Date Filter!!!"}, 400)
            else:

                ongoing_bookings = Bookings.objects \
                    .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                              & Q(entity_type__in=entity_filter) & Q(booking_status=BookingStatus.ongoing.value)))
                pending_bookings = Bookings.objects \
                    .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                              & Q(entity_type__in=entity_filter) & Q(booking_status=BookingStatus.pending.value)))
                cancelled_bookings = Bookings.objects \
                    .filter(Q(Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                              & Q(entity_type__in=entity_filter) & Q(booking_status=BookingStatus.cancelled.value)))

            return HttpResponse({"\nongoing : " + str(len(ongoing_bookings))
                                    , "\npending : " + str(len(pending_bookings))
                                    , "\ncancelled : " + str(len(cancelled_bookings))}, 200)
        else:
            return Response(input_serializer.errors, 400)


def getEntityType(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if entity_filter in entities:
        return [entity_filter]
    return entities


def getTimePeriod(booking_filter):
    if booking_filter == 'Today':
        today = date.today()
        tomorrow = today + timedelta(1)
        return today, tomorrow
    elif booking_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif booking_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        return week, today
    elif booking_filter == 'Month':
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, today
    return None, None


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status
