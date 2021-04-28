from ReviewsRatings.exportapi import *
from Payments.exportapi import *
from Product.exportapi import *
from Coupons.exportapi import *


def get_product_data(product_id_list):
    products = product_data_prices(product_id_list)
    if len(products) == 0:
        return None
    return products


def get_individual_product_data(product_ids):
    product = get_product_data(product_ids)
    return product


def get_coupon_value(coupon_id, user, entity_ids, product_ids, total_money):
    value = coupon_value(coupon_id, user, entity_ids, product_ids, total_money)
    if len(value) == 2:
        return False, "Invalid Coupon"
    return True, value['new_price']


def get_product_ids_total_quantity(product_ids):
    return products_total_quantity(product_ids)


def business_client_review_on_customer(review, rating, booking_id, user):
    data = {'related_id': booking_id, 'comment': review, 'rating': int(rating), 'reviewed_by': user}
    return insert_rating(data)


def get_transaction_details_by_booking_id(booking_id):
    return transaction_details_by_booking_id(booking_id)


def get_review_by_booking_id(booking_id):
    return review_by_booking_id(booking_id)


def get_product_details(product_ids):
    return product_details(product_ids)


def create_transaction(booking_id, entity_id, entity_type, total_money, payment_status, booking_date,total_net_value):
    return new_transaction(booking_id, entity_id, entity_type, total_money, payment_status, booking_date,total_net_value)