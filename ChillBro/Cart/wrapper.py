from Product.exportapi import  get_entity_id_and_entity_type
from Bookings.views import valid_booking, product_details_with_image


def check_valid_booking(product_id, quantity,  start_time, end_time):
    product_list = [{'product_id': product_id, "quantity": quantity}]
    error, product_id =valid_booking(product_list, start_time, end_time)
    if len(error) !=0:
        return False, error
    return True, True


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)


def check_valid_product(product_id):
    return get_entity_id_and_entity_type(product_id)