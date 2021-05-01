from Product.exportapi import  check_cart_product_is_valid_or_not_by_entity_id
from Bookings.views import valid_booking, product_details_with_image


def check_valid_booking(product_id, quantity,  start_time, end_time):
    product_list = [{'product_id': product_id, "quantity": quantity}]
    comment, product_id =valid_booking(product_list, start_time, end_time)
    if len(comment) !=0:
        return False, comment
    return True, True


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)


def check_valid_product(product_id):
    return check_cart_product_is_valid_or_not_by_entity_id(product_id)