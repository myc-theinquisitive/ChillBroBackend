from Bookings.exportapi import get_completed_booking_details_for_entity_ids


def get_completed_bookings_by_entity_id(from_date, to_date, entity_filters, entity_id):
    return get_completed_booking_details_for_entity_ids(from_date, to_date, entity_filters, entity_id)