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
    products = product_data_prices(product_id_list)
    if len(products) == 0:
        return None
    return products


def get_coupon_value(coupon_id, user, entity_ids, product_ids, total_money):
    return coupon_value(coupon_id, user, entity_ids, product_ids, total_money)


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
    return new_transaction({'booking_id':booking_id, 'entity_id': entity_id, 'entity_type': entity_type, \
                            'total_money': total_money, 'payment_status': payment_status, 'booking_date':booking_date,\
                            'total_net_value':total_net_value})


def get_product_id_wise_product_details(product_ids):
    products = get_product_details(product_ids)
    product_id_wise_product_details = defaultdict(dict)
    for product in products:
        product_id_wise_product_details[product["id"]] = product
    return product_id_wise_product_details
