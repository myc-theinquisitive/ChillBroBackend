from django.core.exceptions import ValidationError

def getUserId():
    return 'abcdef'


def checkCouponId(coupon_id):
    coupons=['a','b','c']
    if coupon_id not in coupons:
        raise ValidationError("{} is not valid coupon".format(coupon_id))

def checkProductId(product_id):
    prodcuts=['1','2','3']
    if product_id not in prodcuts:
        raise ValidationError("{} is not valid product".format(product_id))


