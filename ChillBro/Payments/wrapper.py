from Bookings.exportapi import getBookingDetailsForPayments
from datetime import datetime


def getBookingDetailsWithFilters(entity_id, from_date, to_date, entity_filter, status):
    return getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status)


def get_booking_details(booking_id):
    return True, {
        "booking_id": booking_id,
        "entity_id": "123",
        "entity_type": "HOTELS",
        "booking_date": datetime.now(),
        "booking_start": datetime.now()
    }
