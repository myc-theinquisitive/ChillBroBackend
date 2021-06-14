from collections import defaultdict
from Product.exportapi import  get_entity_id_and_entity_type, product_details
from Entity.export_apis import get_entity_type_and_sub_type, entity_details
from Product.Places.export_apis import get_place_details_for_ids


def get_entity_details_of_product(product_id):
    entity_id, entity_type = get_entity_id_and_entity_type(product_id)
    return entity_id, entity_type


def get_product_id_wise_details(product_ids):
    products = product_details(product_ids)

    product_id_wise_details = defaultdict(dict)
    for product in products:
        product_id_wise_details[product["id"]] = product

    return product_id_wise_details


def get_entity_type_and_sub_type_for_entity_id(entity_id):
    return get_entity_type_and_sub_type(entity_id)


def get_entity_id_wise_details(entity_ids):
    entities = entity_details(entity_ids)

    entity_id_wise_details = defaultdict(dict)
    for entity in entities:
        entity_id_wise_details[entity["id"]] = entity

    return entity_id_wise_details


def get_place_id_wise_details(place_ids):
    places = get_place_details_for_ids(place_ids)

    place_id_wise_details = defaultdict(dict)
    for place in places:
        place_id_wise_details[place["id"]] = place

    return place_id_wise_details
