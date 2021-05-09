from Product.exportapi import  check_product_is_valid
from Bookings.exportapi import check_order_is_valid


def is_product_id_valid(product_id):
    return check_product_is_valid(product_id)


def is_order_id_valid(booking_id):
    return check_order_is_valid(booking_id)
