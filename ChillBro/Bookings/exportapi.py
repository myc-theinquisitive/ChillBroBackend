from .models import *
from django.db.models import Sum, Q, FloatField, F
from .serializers import *


def getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status):
    bookings =  Bookings.objects.filter(Q(Q(entity_id=entity_id) \
                                     & Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                     & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))
    serializer = BookingsSerializer(bookings, many = True)
    return serializer.data


def getCompltedBookingDetailsForEntityIds(from_date, to_date, entity_filter, entity_id):
    bookings = CheckOutDetails.objects.select_related('booking') \
                .filter(Q(booking__booking_date__gte=from_date) & Q(booking__booking_date__lte=to_date)\
                & Q(booking__entity_type__in=entity_filter) & Q(booking__entity_id=entity_id))
    all_bookings = {}
    for each_booking in bookings:
        booking= {'booking_id': each_booking.booking_id, 'check_out': each_booking.check_out,
                  'total_money': each_booking.booking.total_money}
        all_bookings[str(each_booking.booking_id)]=booking
    return all_bookings


def bookedCountOfProductId(product_id, from_date, to_date):
    return BookedProducts.objects.select_related('booking') \
            .filter(Q(booking__booking_date__gte = from_date) & Q(booking__booking_date__lte = to_date)\
            & Q(product_id = product_id )).aggregate(count = Sum(F('quantity')))['count']