from .models import *
from django.db.models import Sum, Q, FloatField, F
from .serializers import *


def getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status):
    bookings =  Bookings.objects.filter(Q(Q(entity_id=entity_id) \
                                     & Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                     & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))
    serializer = BookingsSerializer(bookings, many = True)
    return serializer.data

