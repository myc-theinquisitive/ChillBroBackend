from ReviewsRatings.exportapi import *
from Payments.exportapi import *
from Product.exportapi import *
from Coupons.exportapi import *


def get_discounted_value(coupon_id, user, entity_ids, product_ids, total_money):
    return coupon_value(coupon_id, user, entity_ids, product_ids, total_money)


def get_coupon_value(coupon_id, user, entity_ids, product_ids, total_money):
    return coupon_value(coupon_id, user, entity_ids, product_ids, total_money)


def business_client_review_on_customer(review, rating, booking_id, created_by):
    data = {'related_id': booking_id, 'comment': review, 'rating': int(rating), 'created_by': created_by}
    return insert_rating(data)


def get_transaction_details_by_booking_id(booking_id):
    return transaction_details_by_booking_id(booking_id)


def get_review_by_booking_id(booking_id):
    return review_by_booking_id(booking_id)


def get_product_details(product_ids):
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
    product_id_wise_product_details = get_product_id_wise_details(product_ids)
    return product_id_wise_product_details
