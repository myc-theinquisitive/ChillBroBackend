import uuid

from django.db import models
from .validators import checkCouponId, checkProductId
from .constants import BookingStatus, PayStatus, EntityType
from datetime import datetime
from .helpers import get_user_model


# Create your models here.
def getId():
    return str(uuid.uuid4())


class Bookings(models.Model):
    user_model = get_user_model()
    user = models.ForeignKey(user_model, on_delete=models.CASCADE)
    coupon = models.CharField(max_length=36, validators=[checkCouponId], verbose_name="Coupon Id")
    booking_id = models.CharField(max_length=36, primary_key=True, default=getId, verbose_name="Booking Id")
    booking_date = models.DateTimeField(default=datetime.now())
    total_money = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    entity_type = models.CharField(max_length=30,
                                   choices=[(type_of_entity.value, type_of_entity.value) for type_of_entity in
                                            EntityType], default=EntityType.hotels.value)
    booking_status = models.CharField(max_length=30, choices=[(booking_status.value, booking_status.value) for booking_status in BookingStatus],
                                      default=BookingStatus.pending.value)
    payment_status = models.CharField(max_length=30,
                                      choices=[(pay_status.value, pay_status.value) for pay_status in PayStatus],
                                      default=PayStatus.pending.value)

    def __str__(self):
        return (self.booking_id)


class BookedProducts(models.Model):
    booking_id = models.ForeignKey('Bookings', on_delete=models.CASCADE, verbose_name="Booking Id")
    product_id = models.CharField(max_length=36, verbose_name="Product Id")
    entity_id = models.CharField(max_length=36)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    quantity = models.IntegerField()
    product_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_cancelled = models.BooleanField(default=False)
    product_status = models.CharField(max_length=30, choices=[(product_status.value, product_status.value) for product_status in BookingStatus],
                                      default=BookingStatus.pending.value)

    class Meta:
        unique_together = (("booking_id", "product_id"),)

    def __str__(self):
        return "Ordered Product Nº{0}, Nº{1}".format(self.id, self.product_id)
