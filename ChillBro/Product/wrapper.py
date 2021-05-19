from collections import defaultdict
from Bookings.exportapi import booked_count_of_product_id
from Entity.export_apis import get_entity_details_for_entity_ids, is_entity_id_exist, \
    filter_entity_ids_by_city
from ReviewsRatings.exportapi import average_rating_query_for_secondary_related_id, \
    get_secondary_related_id_wise_average_rating


def get_booked_count_of_product_id(product_id, from_date, to_date):
    return booked_count_of_product_id(product_id, from_date, to_date)


def is_entity_id_valid(entity_id):
    return is_entity_id_exist(entity_id)


def get_seller_id_wise_seller_details(seller_ids):
    sellers_details = get_entity_details_for_entity_ids(seller_ids)
    seller_id_wise_seller_details = defaultdict(dict)
    for seller_details in sellers_details:
        seller_id_wise_seller_details[seller_details["id"]] = seller_details
    return seller_id_wise_seller_details


def filter_seller_ids_by_city(seller_ids, city):
    return filter_entity_ids_by_city(seller_ids, city)


def average_rating_query_for_product(product_id):
    return average_rating_query_for_secondary_related_id(product_id)


def get_product_id_wise_average_rating(product_ids):
    product_ratings = get_secondary_related_id_wise_average_rating(product_ids)
    product_id_wise_rating = defaultdict(float)
    for product_rating in product_ratings:
        product_id_wise_rating[product_rating["secondary_related_id"]] = product_rating["avg_rating"]
    return product_id_wise_rating
