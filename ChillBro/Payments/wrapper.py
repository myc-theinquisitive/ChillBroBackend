from Bookings.exportapi import get_booking_details_for_payments


def get_booking_details(entity_id, from_date, to_date, entity_filter, status):
    return get_booking_details_for_payments(entity_id, from_date, to_date, entity_filter, status)

