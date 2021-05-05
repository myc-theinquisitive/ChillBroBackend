from ReviewsRatings.exportapi import *
from Payments.exportapi import *
from collections import defaultdict
from Product.exportapi import *
from Coupons.exportapi import *


def get_discounted_value(coupon_id, product_ids, entity_ids, total_money):
    return True, total_money
    # return False, 0


def get_total_quantity_of_product(product_id):
    return 3


def get_product_data(product_id_list):
    products = product_details(product_id_list)
    if len(products) == 0:
        return None
    return products


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


def create_transaction(booking_id, entity_id, entity_type, total_money, booking_date, booking_start, \
                       total_net_value, paid_to, paid_by):
    return new_transaction({'booking_id':booking_id, 'entity_id': entity_id, 'entity_type': entity_type, \
                            'total_money': total_money, 'booking_date':booking_date,\
                            'booking_start':booking_start, 'total_net_value':total_net_value, \
                            'paid_to':paid_to, 'paid_by':paid_by})


def get_product_id_wise_product_details(product_ids):
    product_id_wise_product_details = get_product_details(product_ids)
    return product_id_wise_product_details
