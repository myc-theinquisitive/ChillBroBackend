from ReviewsRatings.exportapi import insert_rating, review_by_booking_id
from Payments.exportapi import transaction_details_by_booking_id, new_booking_transaction, \
    update_booking_transaction, new_refund_transaction
from Coupons.exportapi import coupon_value
from Entity.export_apis import get_entity_details_for_entity_ids


def get_discounted_value(coupon_id, user, entity_ids, product_ids, product_type, total_money):
    # Product types are same as entity types
    return coupon_value(coupon_id, user, entity_ids, product_ids, [product_type], total_money)


def business_client_review_on_customer(review, rating, booking_id, created_by):
    data = {'related_id': booking_id, 'comment': review, 'rating': int(rating), 'created_by': created_by}
    return insert_rating(data)


def get_transaction_details_by_booking_id(booking_id):
    return transaction_details_by_booking_id(booking_id)


def get_review_by_booking_id(booking_id):
    return review_by_booking_id(booking_id)


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
