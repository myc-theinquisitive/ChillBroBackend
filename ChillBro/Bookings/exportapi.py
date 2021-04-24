from .models import *
from django.db.models import Sum, Q, FloatField, F


def getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status):
    return Bookings.objects.filter(Q(Q(entity_id=entity_id) \
                                     & Q(booking_date__gte=from_date) & Q(booking_date__lte=to_date) \
                                     & Q(entity_type__in=entity_filter) & Q(booking_status__in=status)))


def bookingDetailsByEntityIdByEntityType(entity_type, entity_id):
    return Bookings.objects.total_received_bookings(entity_type, entity_id)


def bookingDetailsByDateByEntityIdByEntityType(from_date, to_date, entity_filter, entity_id):
    return Bookings.objects.received_bookings(from_date, to_date, entity_filter, entity_id)
