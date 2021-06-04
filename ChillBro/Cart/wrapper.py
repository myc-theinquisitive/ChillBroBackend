from Product.exportapi import get_entity_id_and_entity_type
from Coupons.exportapi import coupon_value
from Bookings.exportapi import create_multiple_bookings


def check_valid_booking(product_list, start_time, end_time):
    from Bookings.views import valid_booking
    is_valid, errors = valid_booking(product_list, start_time, end_time)
    return is_valid, errors


def get_product_details_with_image(product_ids):
    from Product.exportapi import product_details_with_image
    return product_details_with_image(product_ids)


def check_valid_product(product_id):
    return get_entity_id_and_entity_type(product_id)


def get_product_id_wise_product_details(product_ids):
    from Product.exportapi import get_product_id_wise_details
    product_id_wise_product_details = get_product_id_wise_details(product_ids)
    return product_id_wise_product_details


def get_discounted_value(coupon_id, user, entity_ids, product_ids, product_type, total_money):
    # Product types are same as entity types
    return coupon_value(coupon_id, user, entity_ids, product_ids, [product_type], total_money)


def create_multiple_bookings_from_cart(all_bookings):
    return create_multiple_bookings(all_bookings)