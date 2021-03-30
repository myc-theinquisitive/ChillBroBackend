from django.db import models
from Coupons.helpers import (get_random_code, get_coupon_code_length, get_user_model)
from .validators import getUserId,checkCouponId,checkProductId
# Create your models here.

class Orders(models.Model):
    # user_model = get_user_model()
    user = models.CharField(max_length=16, default=getUserId, verbose_name="User Id")
    coupon = models.CharField(max_length=16, validators=[checkCouponId  ], verbose_name="Coupon Id")
    booking_id = models.CharField(max_length=16, default=get_random_code, verbose_name="Order Id")
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
        (1, 'Ordered'),
        (2, 'Delivered'),
        (3, 'Cancelled'),
    )
    order_status = models.IntegerField(choices=Status, default=1)
    pay_status = (
        (1, 'Not done'),
        (2, 'Done'),
    )
    payment_status = models.IntegerField(choices=pay_status,default=1)


    def __str__(self):
        return "Orders Booking Nº{0}".format(self.id)

class OrderedProducts(models.Model):
    booking_id = models.ForeignKey('Orders',on_delete=models.CASCADE, verbose_name= "Order Id")
    product_id = models.CharField(max_length=16, validators=[checkProductId], verbose_name="Product Id")
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
        return "Ordered Product Nº{0}, Nº{1}".format(self.id,self.product)

