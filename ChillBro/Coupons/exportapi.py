from .views import *


def coupon_value(coupon_code, user, entity_ids, product_ids, order_value):
    coupon = retrieve_coupon_from_db(coupon_code)
    if coupon:
        validation_data = validate_coupon(coupon=coupon, user=user, entity_ids=entity_ids,
                                          product_ids=product_ids, order_value=order_value)
    else:
        validation_data = {
            "valid": False,
            "message": "Coupon does not exist!"
        }
    if not validation_data['valid']:
        return validation_data

    discounted_value = get_discounted_value(coupon=coupon, order_value=order_value)
    content = {"valid":True, 'discounted_value': discounted_value}
    return content