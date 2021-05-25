from django.db import models
import uuid
from .constants import EntityType
from .helpers import get_user_model
# Create your models here.


def get_id():
    return str(uuid.uuid4())


class Cart(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(max_length=30,
                                   choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in
                                            EntityType], default=EntityType.HOTEL.value)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class CartProducts(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product_id = models.CharField(max_length=36)
    quantity = models.IntegerField()

    def __str__(self):
        return "cart - {} and product - {}".format(self.cart, self.product_id)
