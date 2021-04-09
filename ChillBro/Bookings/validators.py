from django.core.exceptions import ValidationError

from Bookings.wrapper import get_coupons, get_product_data


def get_user_id():
    return 'abcdef'


def check_coupon_id(coupon_id):
    coupons = get_coupons(coupon_id)
    if coupons == None:
        raise ValidationError("{} is not valid coupon".format(coupon_id))

def check_product_id(product_id):
    products = get_product_data(product_id)
    if  products == None:
        raise ValidationError("{} is not valid product".format(product_id))


