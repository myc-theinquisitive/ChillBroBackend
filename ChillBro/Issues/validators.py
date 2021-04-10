from django.core.exceptions import ValidationError
from .wrappers import getProducts, getOrders


def checkProductId(product_id):
    if product_id not in getProducts():
        raise ValidationError("Product {} is not valid product".format(product_id))


def checkOrderId(order_id):
    if order_id not in getOrders():
        raise ValidationError("Order {} is not valid order".format(order_id))
