from .models import CouponUser
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


def validate_allowed_entities_rule(coupon, entity_ids):
    allowed_entities_rule = coupon.ruleset.allowed_entities
    if not allowed_entities_rule.all_entities:
        allowed_entity_ids = allowed_entities_rule.entities
        for entity_id in entity_ids:
            if not entity_id in allowed_entity_ids:
                return False, "Invalid coupon for this Entities!"

    return True, ""


def validate_allowed_products_rule(coupon, product_ids):
    allowed_products_rule = coupon.ruleset.allowed_products
    if not allowed_products_rule.all_products:
        allowed_product_ids = allowed_products_rule.products
        for product_id in product_ids:
            if not product_id in allowed_product_ids:
                return False, "Invalid coupon for this Products!"

    return True, ""


def validate_allowed_users_rule(coupon, user):
    allowed_users_rule = coupon.ruleset.allowed_users
    allowed_user_ids = allowed_users_rule.users
    if not str(user.id) in allowed_user_ids:
        if not allowed_users_rule.all_users:
            return False, "Invalid coupon for this User!"

    return True, ""


def validate_max_uses_rule(coupon, user):
    max_uses_rule = coupon.ruleset.max_uses
    if coupon.times_used >= max_uses_rule.max_uses and not max_uses_rule.is_infinite:
        return False, "Coupon uses exceeded!"

    try:
        coupon_user = CouponUser.objects.get(coupon=coupon, user=user)
        if coupon_user.times_used >= max_uses_rule.uses_per_user:
            return False, "Coupon uses exceeded for this User!"
    except CouponUser.DoesNotExist:
        pass

    return True, ""


def validate_validity_rule(coupon, order_value):
    validity_rule = coupon.ruleset.validity
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


def validate_coupon(coupon, user, entity_ids, product_ids, order_value):
    if not coupon:
        return assemble_invalid_message(message="No coupon provided!")

    if not user:
        return assemble_invalid_message(message="No User provided!")

    valid_allowed_users_rule, message = validate_allowed_users_rule(coupon=coupon, user=user)
    if not valid_allowed_users_rule:
        return assemble_invalid_message(message=message)

    valid_allowed_entities_rule, message = validate_allowed_entities_rule(
        coupon=coupon, entity_ids=entity_ids)
    if not valid_allowed_entities_rule:
        return assemble_invalid_message(message=message)

    valid_allowed_products_rule, message = validate_allowed_products_rule(
        coupon=coupon, product_ids=product_ids)
    if not valid_allowed_products_rule:
        return assemble_invalid_message(message=message)

    valid_max_uses_rule, message = validate_max_uses_rule(coupon=coupon, user=user)
    if not valid_max_uses_rule:
        return assemble_invalid_message(message=message)

    valid_validity_rule, message = validate_validity_rule(coupon=coupon, order_value=order_value)
    if not valid_validity_rule:
        return assemble_invalid_message(message=message)

    return VALID_TEMPLATE
