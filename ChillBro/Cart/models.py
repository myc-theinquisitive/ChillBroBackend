from django.db import models
import uuid
from ChillBro.constants import EntityType, EntitySubType
from .constants import TripType
from .helpers import get_user_model
# Create your models here.


def get_id():
    return str(uuid.uuid4())


class Cart(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    entity_id = models.CharField(max_length=36)
    entity_type = models.CharField(
        max_length=30, choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in EntityType])
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
    size = models.CharField(max_length=10, verbose_name="Size", blank=True, null=True)
    has_sub_products = models.BooleanField(default=False)
    is_combo = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    parent_cart_product = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Parent Care Product Id")

    def __str__(self):
        return "cart - {} and product - {}".format(self.cart, self.product_id)

    class Meta:
        unique_together = (("cart", "product_id", "size", "hidden", "parent_cart_product"),)


class TransportDetails(models.Model):
    cart_product = models.ForeignKey('CartProducts', on_delete=models.CASCADE)
    trip_type = models.CharField(max_length=30, choices=[(trip_type.value, trip_type.value) for trip_type in TripType],
                                 null=True, blank=True)
    pickup_location = models.CharField(max_length=36, blank=True, null=True)
    drop_location = models.CharField(max_length=36, blank=True, null=True)
    km_limit_choosen = models.PositiveIntegerField(default=0)


class EventsDetails(models.Model):
    cart_product = models.ForeignKey('CartProducts', on_delete=models.CASCADE)
    date = models.DateTimeField()
    slot = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    phone_no = models.IntegerField(max_length=10)
    alternate_no = models.IntegerField(max_length=10)
    email = models.CharField(max_length=50)


class EventsPrices(models.Model):
    event_details = models.ForeignKey('EventsDetails', on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    quantity = models.IntegerField(default=0)