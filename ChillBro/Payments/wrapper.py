from Bookings.exportapi import getBookingDetailsForPayments, bookingDetailsByEntityIdByEntityType, \
    bookingDetailsByDateByEntityIdByEntityType


def getBookingDetails(entity_id, from_date, to_date, entity_filter, status):
    return getBookingDetailsForPayments(entity_id, from_date, to_date, entity_filter, status)


def getBookingDetailsByEntityIdByEntityType(entity_type, entity_id):
    return bookingDetailsByEntityIdByEntityType(entity_type, entity_id)


def getBookingDetailsByDateByEntityIdByEntityType(from_date, to_date, entity_filter, entity_id):
    return bookingDetailsByDateByEntityIdByEntityType(from_date, to_date, entity_filter, entity_id)



