from django.core.exceptions import ValidationError

from Bookings.wrapper import getCoupons, getProductData



def checkCouponId(coupon_id):
    coupons = getCoupons(coupon_id)
    if coupons == None:
        raise ValidationError("{} is not valid coupon".format(coupon_id))

def checkProductId(product_id):
    products = getProductData(product_id)
    if  products == None:
        raise ValidationError("{} is not valid product".format(product_id))


