from Address.exportapi import *
from Product.exportapi import total_products_count_in_entities


def post_create_address(city,pincode):
    return create_address({'city':city, 'pincode':pincode})


def get_total_products_count_in_entities(entity_ids):
    return total_products_count_in_entities(entity_ids)
