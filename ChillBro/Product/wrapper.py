from collections import defaultdict
from Bookings.exportapi import booked_count_of_product_id
from Entity.export_apis import get_entity_details_for_entity_ids, is_entity_id_exist, \
    filter_entity_ids_by_city
from ReviewsRatings.exportapi import average_rating_query_for_secondary_related_id, \
    get_secondary_related_id_wise_average_rating, get_rating_stats_for_secondary_related_id, \
    get_rating_type_wise_average_rating_for_secondary_related_id, get_latest_ratings_for_secondary_related_id
from WishList.exportapis import get_wishlist_product_ids
from django.conf import settings
from .models import Product


def get_booked_count_of_product_id(product_id, from_date, to_date):
    return booked_count_of_product_id(product_id, from_date, to_date)


def is_entity_id_valid(entity_id):
    if settings.MYC_ID == entity_id:
        return True
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
    product_id_wise_rating = defaultdict(dict)
    for product_rating in product_ratings:
        product_id_wise_rating[product_rating["secondary_related_id"]] = product_rating
        product_rating.pop("secondary_related_id", None)
    for product_id in product_ids:
        if not product_id_wise_rating[product_id]:
            product_id_wise_rating[product_id] = {
                "avg_rating": 0,
                "total_reviews": 0
            }
    return product_id_wise_rating


def get_product_id_wise_wishlist_status(user_id, product_ids):
    product_id_wise_wishlist_status = defaultdict(bool)
    wishlist_product_ids = get_wishlist_product_ids(user_id, product_ids)
    for product_id in wishlist_product_ids:
        product_id_wise_wishlist_status[product_id] = True
    return product_id_wise_wishlist_status


def get_rating_wise_review_details_for_product(product_id):
    return get_rating_stats_for_secondary_related_id(product_id)


def get_rating_type_wise_average_rating_for_product(product_id):
    return get_rating_type_wise_average_rating_for_secondary_related_id(product_id)


def get_latest_ratings_for_product(product_id):
    return get_latest_ratings_for_secondary_related_id(product_id)


def get_address_id_of_product(product_ids):
    try:
        products = Product.objects.filter(id__in=product_ids)  # .values_list('seller_id')
        entity_ids = []
        entity_product = {}
        for product in products:
            entity_product[product.seller_id] = product.id
            entity_ids.append(product.seller_id)

        entity_details = get_entity_details_for_entity_ids(entity_ids)
        print(entity_details,'==============entity_details================')
        product_address = {}
        if len(entity_details) != 0:
            for entity in entity_details:
                product_id = entity_product[entity['id']]
                product_address[product_id] = entity['address']

            return product_address

        return None
    except Product.DoesNotExist:
        return None
