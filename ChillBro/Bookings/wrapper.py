from ReviewsRatings.exportapi import *
from Payments.models import *
from Payments.exportapi import *
from collections import defaultdict


def get_product_details(product_ids):
    product_details = []
    for product_id in product_ids:
        product = {
            "id": product_id,
            "price": 100.0
        }
        product_details.append(product)
    return product_details


def get_product_id_wise_product_details(product_ids):
    products = get_product_details(product_ids)
    product_id_wise_product_details = defaultdict(dict)
    for product in products:
        product_id_wise_product_details[product["id"]] = product
    return product_id_wise_product_details


def get_discounted_value(coupon_id, product_ids, entity_ids, total_money):
    return True, total_money
    # return False, 0


def getCoupons(coupon_id):
    coupons = ['df8966f9-f6ce-4a46-9a00-80ac3988f821', 'df8966f9-f6ce-4a46-9a00-80ac3988f822',
               'df8966f9-f6ce-4a46-9a00-80ac3988f823']
    if coupon_id in coupons:
        return coupon_id
    return None


def get_total_quantity_of_product(product_id):
    return 3


def businessClientReviewOnCustomer(review, rating, booking_id, user):
    data = {'related_id': booking_id, 'comment': review, 'rating': int(rating), 'reviewed_by': user}
    return insertRating(data)


def getTransactionDetailsByBookingId(booking_id):
    return transactionDetailsByBookingId(booking_id)


def getTransactionDetails():
    return TransactionDetails.objects.all()


def getReviewByBookingId(booking_id):
    return ReviewByBookingId(booking_id)


def get_products_details(product_ids):
    return { "df8966f9-f6ce-4a46-9a00-80ac3988f818": {'name': 'xyz', 'type': 'type'},
             "df8966f9-f6ce-4a46-9a00-80ac3988f819": {'name': 'xyz', 'type': 'type'},
             "df8966f9-f6ce-4a46-9a00-80ac3988f820": {'name': 'xyz', 'type': 'type'}}


def create_transaction(booking_id, entity_id, entity_type, total_money, booking_date, booking_start, paid_to, paid_by):
    return newTransaction(booking_id, entity_id, entity_type, total_money, booking_date, booking_start, paid_to, paid_by)
