import uuid

from django.db import models
from Coupons.helpers import (get_random_code, get_coupon_code_length, get_user_model)
from .validators import get_user_id,check_coupon_id,check_product_id
# Create your models here.
def get_order_id():
    return str(uuid.uuid4())

class Orders(models.Model):
    # user_model = get_user_model()
    user = models.CharField(max_length=16, default=get_user_id, verbose_name="User Id")
    coupon = models.CharField(max_length=16, validators=[check_coupon_id  ], verbose_name="Coupon Id")
    booking_id = models.CharField(max_length=50, primary_key = True,default=get_order_id, verbose_name="Order Id")
    booking_date = models.DateTimeField()
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    type=(
        (1,'Hotels'),
        (2,'Transport'),
        (3,'Rentals'),
        (4,'Resorts'),
        (5,'Events'),
    )
    entity_type=models.IntegerField(choices=type,default=1)

    Status = (
        (1, 'PENDING'),
        (2, 'ONGOING'),
        (3, 'CANCELLED'),
        (4, 'DONE'),
    )
    order_status = models.IntegerField(choices=Status, default=1)
    pay_status = (
        (1, 'PENDING'),
        (2, 'DONE'),
    )
    payment_status = models.IntegerField(choices=pay_status,default=1)


    def __str__(self):
        return (self.booking_id)

class OrderedProducts(models.Model):
    booking_id = models.ForeignKey('Orders',on_delete=models.CASCADE, verbose_name= "Order Id")
    product_id = models.CharField(max_length=16, validators=[check_product_id], verbose_name="Product Id")
    # entity = models.OneToOneField(MyEntity, on_delete=models.CASCADE, null=True, verbose_name="Entity Id")
    entity = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    quantity = models.IntegerField()
    product_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_cancelled = models.BooleanField(default=False)


    class Meta:
        unique_together = (("booking_id", "product_id"),)


    def __str__(self):
        return "Ordered Product Nº{0}, Nº{1}".format(self.id,self.product_id)

