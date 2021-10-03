from ReviewsRatings.exportapi import insert_business_client_review_for_customer, \
    business_client_review_for_customer_by_booking_id
from Payments.exportapi import transaction_details_by_booking_id, new_booking_transaction, \
    update_booking_transaction, new_refund_transaction
from Coupons.exportapi import coupon_value
from Entity.export_apis import get_entity_details_for_entity_ids
from Address.exportapi import create_address, update_address, validate_address


def business_client_review_on_customer(review, rating, booking_id, created_by):
    data = {'related_id': booking_id, 'comment': review, 'rating': int(rating), 'created_by': created_by}
    return insert_business_client_review_for_customer(data)


def get_coupon_value(coupon_code, user, entity_ids, product_ids, product_types, order_value):
    return coupon_value(coupon_code, user, entity_ids, product_ids, product_types, order_value)


def get_transaction_details_by_booking_id(booking_id):
    return transaction_details_by_booking_id(booking_id)


def get_business_client_review_by_booking_id(booking_id):
    return business_client_review_for_customer_by_booking_id(booking_id)


def get_product_details(product_ids):
    from Product.exportapi import product_details
    return product_details(product_ids)


def create_booking_transaction(transaction_data):
    return new_booking_transaction(transaction_data)


def update_booking_transaction_in_payment(booking_id, is_complete_cancellation, total_amount_reduced,
                                          net_amount_reduced, commission_amount_reduced):
    update_booking_transaction(booking_id, is_complete_cancellation, total_amount_reduced,
                               net_amount_reduced, commission_amount_reduced)


def create_refund_transaction(transaction_data):
    return new_refund_transaction(transaction_data)


def get_product_id_wise_product_details(product_ids):
    from Product.exportapi import get_product_id_wise_details
    product_id_wise_product_details = get_product_id_wise_details(product_ids)
    return product_id_wise_product_details
    
    
def get_entity_details(entity_ids):
    return get_entity_details_for_entity_ids(entity_ids)


def get_product_prices_by_duration(products):
    from Product.exportapi import get_product_final_prices
    return get_product_final_prices(products)


def get_product_net_price(excess_price, product_type):
    from Product.exportapi import calculate_product_excess_net_price
    return calculate_product_excess_net_price(excess_price, product_type)


def is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details):
    from Cart.exportapi import check_is_product_valid
    return check_is_product_valid(product_details, product_id, quantity, all_sizes, combo_product_details)


def check_valid_duration(product_ids, start_time, end_time):
    from Product.exportapi import check_valid_duration_for_products
    return check_valid_duration_for_products(product_ids, start_time, end_time)


def check_valid_address(address):
    return validate_address(address)


def combine_all_products(product_id, size, quantity, combo_product_details,product_details):
    from Cart.exportapi import form_all_products
    return form_all_products(product_id, size, quantity, combo_product_details,product_details)


def entity_id_and_entity_type(product_id):
    from Product.exportapi import get_entity_id_and_entity_type
    return get_entity_id_and_entity_type(product_id)


def get_product_price_values(group_product_ids_by_type, group_product_details_by_type):
    from Product.exportapi import get_product_values
    return get_product_values(group_product_ids_by_type, group_product_details_by_type)


def post_create_address(address_data):
    return create_address(address_data)


def check_valid_address(address):
    return validate_address(address)