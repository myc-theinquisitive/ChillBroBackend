from .models import Coupon, CouponUser
from django.utils import timezone


INVALID_TEMPLATE = {
    "valid": False,
    "message": ""
}

VALID_TEMPLATE = {
    "valid": True
}


def assemble_invalid_message(message=""):
    response = INVALID_TEMPLATE
    response['message'] = message
    return response


def validate_allowed_entities_rule(coupon_object, entity):
    allowed_entities_rule = coupon_object.ruleset.allowed_entities
    if not entity in allowed_entities_rule.entities.all():
        if not allowed_entities_rule.all_entities:
            return False, "Invalid coupon for this Entity!"

    return True, ""


def validate_allowed_users_rule(coupon_object, user):
    allowed_users_rule = coupon_object.ruleset.allowed_users
    if not user in allowed_users_rule.users.all():
        if not allowed_users_rule.all_users:
            return False, "Invalid coupon for this User!"

    return True, ""


def validate_max_uses_rule(coupon_object, user):
    max_uses_rule = coupon_object.ruleset.max_uses
    if coupon_object.times_used >= max_uses_rule.max_uses and not max_uses_rule.is_infinite:
        return False, "Coupon uses exceeded!"

    try:
        coupon_user = CouponUser.objects.get(user=user)
        if coupon_user.times_used >= max_uses_rule.uses_per_user:
            return False, "Coupon uses exceeded for this User!"
    except CouponUser.DoesNotExist:
        pass

    return True, ""


def validate_validity_rule(coupon_object, order_value):
    validity_rule = coupon_object.ruleset.validity
    if timezone.now() > validity_rule.expiration_date:
        return False, "Coupon Expired!"

    if order_value < validity_rule.minimum_order_value:
        return False, "Minimum order value to avail the coupon is {0}".format(validity_rule.minimum_order_value)

    if not validity_rule.is_active:
        return False, "Coupon is not active"

    return True, ""


def validate_coupon(coupon_code, user, entity, order_value):
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

    valid_allowed_entities_rule, message = validate_allowed_entities_rule(coupon_object=coupon_object, entity=entity)
    if not valid_allowed_entities_rule:
        return assemble_invalid_message(message=message)

    valid_max_uses_rule, message = validate_max_uses_rule(coupon_object=coupon_object, user=user)
    if not valid_max_uses_rule:
        return assemble_invalid_message(message=message)

    valid_validity_rule, message = validate_validity_rule(coupon_object=coupon_object, order_value=order_value)
    if not valid_validity_rule:
        return assemble_invalid_message(message=message)

    return VALID_TEMPLATE
