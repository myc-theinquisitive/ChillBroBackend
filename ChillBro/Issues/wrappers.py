from Product.exportapi import  check_product_is_valid
from Bookings.exportapi import check_order_is_valid
from ReviewsRatings.exportapi import rating_and_comment_for_related_ids
from collections import defaultdict


def is_product_id_valid(product_id):
    return check_product_is_valid(product_id)


def is_order_id_valid(booking_id):
    return check_order_is_valid(booking_id)


def get_issue_id_wise_ratings(issue_ids):
    ratings = rating_and_comment_for_related_ids(issue_ids)
    issue_id_wise_ratings = defaultdict(dict)
    for rating in ratings:
        issue_id_wise_ratings[rating["related_id"]] = rating
        rating.pop("related_id", None)
    return issue_id_wise_ratings
