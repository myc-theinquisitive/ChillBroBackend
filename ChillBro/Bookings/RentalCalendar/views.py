from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RentBooking
from .serializers import RentBookingSerializer, RentBookingIdSerializer, RentBookingWithQuantitySerializer, \
    ProductAvailabilitySerializer, ProductBookingSerializer
from django.db.models import Q
from rest_framework import generics
import threading
from datetime import datetime, timedelta
from .helpers import get_date_format
from ..models import OrderedProducts

# Lock for creating a new booking or updating the booking timings
_booking_lock = threading.Lock()


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


def get_bookings_of_product(product_id, start_time, end_time, is_cancelled=False, order_by='start_time'):

    # getting active booking on the same product with in the new booking timings
    #full doubtsss
    return OrderedProducts.objects\
        .filter(product_id=product_id, is_cancelled=is_cancelled)\
        .filter(
            Q(Q(start_time__lte=start_time) & Q(end_time__gt=start_time)) |
            Q(Q(start_time__lt=end_time) & Q(end_time__gte=end_time)) |
            Q(Q(start_time__lte=start_time) & Q(end_time__gte=end_time)) |
            Q(Q(start_time__gte=start_time) & Q(end_time__lte=end_time))
        ).order_by(order_by)


def valid_booking(product_id, product_quantity, start_time, end_time):

    if start_time >= end_time:
        return False

    if product_quantity <= 0:
        return False

    bookings = get_bookings_of_product(product_id, start_time, end_time)
    return False if len(bookings) >= product_quantity else True


def create_booking(booking_id, product_id, product_quantity, start_time, end_time):
    with _booking_lock:
        if not valid_booking(product_id, product_quantity, start_time, end_time):
            return Response({"message": "Booking Not Allowed"}, 400)

        try:
            OrderedProducts.objects.create(booking_id=booking_id, product_id=product_id,
                                       start_time=start_time, end_time=end_time)
        except:
            return Response({"message": "Exception in Booking Creation: Product & Booking Id should be unique"}, 400)

    return Response({"message": "Booking Created"}, 200)


def update_booking(booking_id, product_id, product_quantity, start_time, end_time):
    with _booking_lock:
        # increasing product quantity by 1 as current booking is also considered as part of validation
        if not valid_booking(product_id, product_quantity+1, start_time, end_time):
            return Response({"message": "Booking Not Allowed"}, 400)

        OrderedProducts.objects.filter(booking_id=booking_id, product_id=product_id) \
            .update(start_time=start_time, end_time=end_time)

    return Response({"message": "Booking Updated"}, 200)


def cancel_booking(booking_id, product_id):
    OrderedProducts.objects.filter(booking_id=booking_id, product_id=product_id)\
        .update(is_cancelled=True)
    return Response({"message": "Booking Cancelled"}, 200)


def product_availability(product_id, product_quantity, start_time, end_time):
    bookings = get_bookings_of_product(product_id, start_time, end_time)

    HOUR = timedelta(hours=1)
    datetime_format = get_date_format()
    hours_dic = {}

    # converting to datetime objects
    start_time = datetime.strptime(start_time, datetime_format)
    end_time = datetime.strptime(end_time, datetime_format)

    start_hour = datetime(start_time.year, start_time.month, start_time.day, start_time.hour, 0, 0)
    end_hour = start_hour + HOUR
    while start_hour < end_time:
        start_hour_key = start_hour.strftime(datetime_format)
        end_hour_key = end_hour.strftime(datetime_format)
        hours_dic[(start_hour_key, end_hour_key)] = product_quantity
        start_hour = end_hour
        end_hour += HOUR

    for booking in bookings:
        booking_start_time = booking.start_time.strftime(datetime_format)
        booking_end_time = booking.end_time.strftime(datetime_format)
        for start_hour_key, end_hour_key in hours_dic:
            if are_overlapping_time_spans(booking_start_time, booking_end_time, start_hour_key, end_hour_key):
                hours_dic[(start_hour_key, end_hour_key)] -= 1

    availabilities = []
    for start_hour_key, end_hour_key in hours_dic:
        availability = {
            "start_hour": start_hour_key,
            "end_hour": end_hour_key,
            "available_count": hours_dic[(start_hour_key, end_hour_key)]
        }
        availabilities.append(availability)
    return Response({"availabilities": availabilities}, 200)


class CreateUpdateRentalBooking(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = RentBookingWithQuantitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        booking_id = serializer.data["booking_id"]
        product_id = serializer.data["product_id"]
        product_quantity = serializer.data["product_quantity"]
        start_time = serializer.data["start_time"]
        end_time = serializer.data["end_time"]

        return create_booking(booking_id=booking_id, product_id=product_id, product_quantity=product_quantity,
                              start_time=start_time, end_time=end_time)

    def put(self, request, format=None):
        serializer = RentBookingWithQuantitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        booking_id = serializer.data["booking_id"]
        product_id = serializer.data["product_id"]
        product_quantity = serializer.data["product_quantity"]
        start_time = serializer.data["start_time"]
        end_time = serializer.data["end_time"]

        return update_booking(booking_id=booking_id, product_id=product_id, product_quantity=product_quantity,
                              start_time=start_time, end_time=end_time)


class CancelRentalBooking(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = RentBookingIdSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        booking_id = serializer.data["booking_id"]
        product_id = serializer.data["product_id"]

        return cancel_booking(booking_id=booking_id, product_id=product_id)


class GetProductAvailability(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        serializer = ProductAvailabilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        product_id = serializer.data["product_id"]
        product_quantity = serializer.data["product_quantity"]
        start_time = serializer.data["start_time"]
        end_time = serializer.data["end_time"]

        return product_availability(product_id=product_id, product_quantity=product_quantity,
                                    start_time=start_time, end_time=end_time)


class RentalBookingList(generics.ListAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = OrderedProducts.objects.all()
    serializer_class = RentBookingSerializer


class ProductBookingList(APIView):
    # permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, format=None):
        serializer = ProductBookingSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.data["product_id"]
            start_time = serializer.data["start_time"]
            end_time = serializer.data["end_time"]

            bookings = get_bookings_of_product(product_id=product_id, start_time=start_time, end_time=end_time)
            output_serializer = RentBookingSerializer(bookings, many=True)
            return Response(output_serializer.data)
        else:
            return Response(serializer.errors, 400)


class CancelledBookingList(APIView):
    # permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, format=None):
        serializer = ProductBookingSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.data["product_id"]
            start_time = serializer.data["start_time"]
            end_time = serializer.data["end_time"]

            bookings = get_bookings_of_product(product_id=product_id, start_time=start_time,
                                               end_time=end_time, is_cancelled=True)
            output_serializer = RentBookingSerializer(bookings, many=True)
            return Response(output_serializer.data)
        else:
            return Response(serializer.errors, 400)

