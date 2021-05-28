from Product.exportapi import  get_entity_id_and_entity_type, product_details_with_image
from Entity.export_apis import get_entity_type_and_sub_type


def getEntityDetailsOfProduct(product_id):
    entity_id, entity_type = get_entity_id_and_entity_type(product_id)
    return entity_id, entity_type


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)


def get_entity_type_and_sub_type_for_entity_id(entity_id):
    return get_entity_type_and_sub_type(entity_id)
