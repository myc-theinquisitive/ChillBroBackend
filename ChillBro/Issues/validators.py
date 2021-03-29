from django.core.exceptions import ValidationError

def checkProductId(product_id):
    prodcuts=['1','2','3']
    if product_id not in prodcuts:
        raise ValidationError("Product {} is not valid product".format(product_id))

def checkOrderId(order_id):
    orders=['1','2','3']
    if order_id not in orders:
        raise ValidationError("Order {} is not valid order".format(order_id))