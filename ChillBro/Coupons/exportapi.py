from .views import *


def coupon_value(coupon_code, user, entity_ids, product_ids, product_types, order_value):
    coupon = retrieve_coupon_from_db(coupon_code)
    if coupon:
        validation_data = validate_coupon(coupon=coupon, user=user, entity_ids=entity_ids,
                                          product_ids=product_ids, product_types=product_types,
                                          order_value=order_value)
        if not validation_data["valid"]:
            validation_data = {
                "is_valid": False,
                "errors": validation_data["message"],
                "discounted_value": None
            }
            return validation_data

    else:
        validation_data = {
            "is_valid": False,
            "errors": "Coupon does not exist!",
            "discounted_value": None
        }
        return validation_data

    discounted_value = get_discounted_value(coupon=coupon, order_value=order_value)
    content = {"is_valid": True, "errors": None, 'discounted_value': discounted_value}
    return content
