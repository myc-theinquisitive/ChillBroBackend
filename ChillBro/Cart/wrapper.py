from Product.exportapi import  check_cart_product_is_valid_or_not_by_entity_id
from Bookings.views import valid_booking, product_details_with_image


def valid_product(product_id, quantity,  start_time, end_time):
    entity_id, entity_type = check_cart_product_is_valid_or_not_by_entity_id(product_id)
    if entity_id is None and entity_type is None:
        return None, "Product Doen't exit"
    product_list = [{'product_id': product_id, "quantity": quantity}]

    comment, product_id =valid_booking(product_list, start_time, end_time)
    if len(comment) !=0:
        return None, comment
    else:
        return entity_id, entity_type


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)