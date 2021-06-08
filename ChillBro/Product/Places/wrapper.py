from Address.exportapi import create_address, update_address, get_address_details, filter_by_city
from ReviewsRatings.exportapi import average_rating_query_for_secondary_related_id, \
    get_secondary_related_id_wise_average_rating
from collections import defaultdict


def post_create_address(address_data):
    return create_address(address_data)


def update_address_for_address_id(address_id, address_data):
    return update_address(address_id, address_data)


def get_address_details_for_address_ids(address_ids):
    return get_address_details(address_ids)


def filter_address_ids_by_city(address_ids, city):
    return filter_by_city(address_ids, city)


def average_rating_query_for_place(place_id):
    return average_rating_query_for_secondary_related_id(place_id)


def get_place_id_wise_average_rating(place_ids):
    place_ratings = get_secondary_related_id_wise_average_rating(place_ids)
    place_id_wise_rating = defaultdict(dict)
    for place_rating in place_ratings:
        place_id_wise_rating[place_rating["secondary_related_id"]] = place_rating
        place_rating.pop("secondary_related_id", None)
    for place_id in place_ids:
        if not place_id_wise_rating[place_id]:
            place_id_wise_rating[place_id] = {
                "avg_rating": 0,
                "total_reviews": 0
            }
    return place_id_wise_rating
