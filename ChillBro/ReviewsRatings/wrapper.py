from Bookings.exportapi import complteBookingDetailsByEntityId


def getCompletedBookingsByEntityId(from_date, to_date, entity_filters, entity_id):
    return complteBookingDetailsByEntityId(from_date, to_date, entity_filters, entity_id)