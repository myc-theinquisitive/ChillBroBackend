from django.core.exceptions import ValidationError
from .wrappers import orderExists,productExists


def checkProductId(product_id):
    if not productExists(product_id):
        raise ValidationError("Product {} is not valid product".format(product_id))


def checkOrderId(order_id):
    if not orderExists(order_id):
        raise ValidationError("Order {} is not valid order".format(order_id))
