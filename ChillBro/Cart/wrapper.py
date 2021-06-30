from collections import defaultdict

from Product.exportapi import get_entity_id_and_entity_type
from Coupons.exportapi import coupon_value
from Bookings.exportapi import create_multiple_bookings
from Entity.export_apis import get_entity_type_and_sub_type
from Address.exportapi import create_address, update_address, validate_address


def check_valid_booking(product_list, start_time, end_time):
    from Bookings.views import valid_booking
    is_valid, errors = valid_booking(product_list, start_time, end_time)
    return is_valid, errors


def get_product_details_with_image(product_ids):
    from Product.exportapi import product_details
    all_product_details = defaultdict()
    products = product_details(product_ids)
    for each_product in products:
        all_product_details[each_product["id"]] = each_product
    return all_product_details


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


def get_entity_type_and_sub_type_for_entity_id(entity_id):
    return get_entity_type_and_sub_type(entity_id)


def post_create_address(address_data):
    return create_address(address_data)


def check_valid_duration(product_ids, start_time, end_time):
    from Product.exportapi import check_valid_duration_for_products
    return check_valid_duration_for_products(product_ids, start_time, end_time)


def get_product_price_values(group_product_ids_by_type, group_product_details_by_type):
    from Product.exportapi import get_product_values
    return get_product_values(group_product_ids_by_type, group_product_details_by_type)


def update_address_details(address_id, address_data):
    return update_address(address_id, address_data)


def check_valid_address(address):
    return validate_address(address)