from datetime import timedelta, datetime
from django.db.models import Q, Sum
from rest_framework.response import Response
from .helpers import get_date_format
from .models import BookedProducts
from .wrapper import get_product_id_wise_product_details


def get_total_bookings_of_product_in_duration(product_id, start_time, end_time, product_size):

    return BookedProducts.objects.active().select_related('booking') \
        .filter(product_id=product_id, size=product_size) \
        .filter(
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gt=start_time)) |
        Q(Q(booking__start_time__lt=end_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__lte=start_time) & Q(booking__end_time__gte=end_time)) |
        Q(Q(booking__start_time__gte=start_time) & Q(booking__end_time__lte=end_time))
    )


def get_total_bookings_count_of_product_in_duration(product_id, start_time, end_time, product_size):
    bookings_count = get_total_bookings_of_product_in_duration(product_id, start_time, end_time, product_size) \
        .aggregate(sum=Sum('quantity'))['sum']
    if bookings_count is None:
        return 0
    return bookings_count


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


def product_availability_per_hour(product_id, start_time, end_time, product_size):
    booked_products = get_total_bookings_of_product_in_duration(product_id, start_time, end_time, product_size)
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
