from Product.exportapi import  check_cart_product_is_valid_or_not_by_entity_id, product_details_with_image


def getEntityDetailsOfProduct(product_id):
    entity_id, entity_type = check_cart_product_is_valid_or_not_by_entity_id(product_id)
    return entity_id, entity_type


def get_product_details_with_image(product_ids):
    return product_details_with_image(product_ids)