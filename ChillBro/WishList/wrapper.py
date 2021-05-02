from Product.exportapi import  get_entity_id_and_entity_type, product_details_with_image


def getEntityDetailsOfProduct(product_id):
    entity_id, entity_type = get_entity_id_and_entity_type(product_id)
    return entity_id, entity_type


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)