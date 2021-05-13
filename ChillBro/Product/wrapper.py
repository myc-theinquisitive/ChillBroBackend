from collections import defaultdict

from Bookings.exportapi import booked_count_of_product_id
from Entity.export_apis import get_entity_details_for_entity_ids, is_entity_id_exist


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
