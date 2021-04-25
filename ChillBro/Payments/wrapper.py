from Bookings.exportapi import getBookingDetailsForPayments


def getBookingDetails(entity_id, from_date, to_date, entity_filter, status):
    return getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status)

