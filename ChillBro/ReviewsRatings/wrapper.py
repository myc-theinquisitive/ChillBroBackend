from Bookings.exportapi import getCompltedBookingDetailsForEntityIds


def getCompletedBookingsByEntityId(from_date, to_date, entity_filters, entity_id):
    return getCompltedBookingDetailsForEntityIds(from_date, to_date, entity_filters, entity_id)