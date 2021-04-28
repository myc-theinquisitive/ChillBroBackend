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
        content = {'message': validation_data['message']}
        return content

    new_price = get_discounted_value(coupon=coupon, order_value=order_value)
    content = {'new_price': new_price}
    return content