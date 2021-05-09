from django.db.models import Sum, F
from .serializers import *


def get_booking_details_for_payments(entity_id, from_date, to_date, entity_filter, status):
    bookings = Bookings.objects.filter(Q(Q(entity_id=entity_id)
                                         & Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date)
                                         & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))
    serializer = BookingsSerializer(bookings, many=True)
    return serializer.data


def get_completed_booking_details_for_entity_ids(entity_filter, entity_id):
    bookings = CheckOutDetails.objects.select_related('booking')\
                .filter(Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id=entity_id))
    all_bookings = {}
    for each_booking in bookings:
        booking = {'booking_id': each_booking.booking_id, 'check_out': each_booking.check_out,
                   'total_money': each_booking.booking.total_money}
        all_bookings[str(each_booking.booking_id)]=booking
    return all_bookings


def booked_count_of_product_id(product_id, from_date, to_date):
    booked_count = BookedProducts.objects.select_related('booking')\
            .filter(Q(booking__booking_date__gte=from_date) & Q(booking__booking_date__lte=to_date)
                    & Q(product_id=product_id)).aggregate(count=Sum(F('quantity')))['count']
    if not booked_count:
        return 0
    return booked_count


def check_order_is_valid(booking_id):
    try:
        booking = Bookings.objects.get(id=booking_id)
        return  True
    except:
        return False
