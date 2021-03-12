from .models import Coupon, CouponUser
from django.utils import timezone


INVALID_TEMPLATE = {
    "valid": False,
    "message": ""
}

VALID_TEMPLATE = {
    "valid": True,
    "message": "Valid Coupon!"
}


def assemble_invalid_message(message=""):
    response = INVALID_TEMPLATE
    response['message'] = message
    return response


def validate_allowed_entities_rule(coupon_object, entity_ids):
    allowed_entities_rule = coupon_object.ruleset.allowed_entities
    if not allowed_entities_rule.all_entities:
        allowed_entity_ids = allowed_entities_rule.entities
        for entity_id in entity_ids:
            if not entity_id in allowed_entity_ids:
                return False, "Invalid coupon for this Entities!"

    return True, ""


def validate_allowed_products_rule(coupon_object, product_ids):
    allowed_products_rule = coupon_object.ruleset.allowed_products
    if not allowed_products_rule.all_products:
        allowed_product_ids = allowed_products_rule.products
        for product_id in product_ids:
            if not product_id in allowed_product_ids:
                return False, "Invalid coupon for this Products!"

    return True, ""


def validate_allowed_users_rule(coupon_object, user):
    allowed_users_rule = coupon_object.ruleset.allowed_users
    allowed_user_ids = allowed_users_rule.users
    if not str(user.id) in allowed_user_ids:
        if not allowed_users_rule.all_users:
            return False, "Invalid coupon for this User!"

    return True, ""


def validate_max_uses_rule(coupon_object, user):
    max_uses_rule = coupon_object.ruleset.max_uses
    if coupon_object.times_used >= max_uses_rule.max_uses and not max_uses_rule.is_infinite:
        return False, "Coupon uses exceeded!"

    try:
        coupon_user = CouponUser.objects.get(coupon=coupon_object, user=user)
        if coupon_user.times_used >= max_uses_rule.uses_per_user:
            return False, "Coupon uses exceeded for this User!"
    except CouponUser.DoesNotExist:
        pass

    return True, ""


def validate_validity_rule(coupon_object, order_value):
    validity_rule = coupon_object.ruleset.validity
    current_time = timezone.now()

    if validity_rule.start_date and validity_rule.start_date > current_time:
        return False, "Coupon Not Active YET!"

    if validity_rule.end_date and current_time > validity_rule.end_date:
        return False, "Coupon Expired!"

    if order_value < validity_rule.minimum_order_value:
        return False, "Minimum order value to avail the coupon is {0}".format(validity_rule.minimum_order_value)

    if not validity_rule.is_active:
        return False, "Coupon is not active"

    return True, ""


def validate_coupon(coupon_code, user, entity_ids, product_ids, order_value):
    if not coupon_code:
        return assemble_invalid_message(message="No coupon code provided!")

    if not user:
        return assemble_invalid_message(message="No User provided!")

    try:
        coupon_object = Coupon.objects.get(code=coupon_code)
    except Coupon.DoesNotExist:
        return assemble_invalid_message(message="Coupon does not exist!")

    valid_allowed_users_rule, message = validate_allowed_users_rule(coupon_object=coupon_object, user=user)
    if not valid_allowed_users_rule:
        return assemble_invalid_message(message=message)

    valid_allowed_entities_rule, message = validate_allowed_entities_rule(
        coupon_object=coupon_object, entity_ids=entity_ids)
    if not valid_allowed_entities_rule:
        return assemble_invalid_message(message=message)

    valid_allowed_products_rule, message = validate_allowed_products_rule(
        coupon_object=coupon_object, product_ids=product_ids)
    if not valid_allowed_products_rule:
        return assemble_invalid_message(message=message)

    valid_max_uses_rule, message = validate_max_uses_rule(coupon_object=coupon_object, user=user)
    if not valid_max_uses_rule:
        return assemble_invalid_message(message=message)

    valid_validity_rule, message = validate_validity_rule(coupon_object=coupon_object, order_value=order_value)
    if not valid_validity_rule:
        return assemble_invalid_message(message=message)

    return VALID_TEMPLATE
