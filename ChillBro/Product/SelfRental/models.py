from django.db import models
import uuid


def get_id():
    return str(uuid.uuid4())


class SelfRental(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="self_rental_product",
                                verbose_name="Vehicle")
    excess_price_per_hour = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class SelfRentalDistancePrice(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    km_limit = models.PositiveIntegerField()
    excess_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_infinity = models.BooleanField(default=False)
    self_rental = models.ForeignKey('SelfRental', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('self_rental', 'km_limit')


class SelfRentalDurationDetails(models.Model):
    min_hour_duration = models.PositiveIntegerField(default=1)
    max_hour_duration = models.PositiveIntegerField(default=24)
    min_day_duration = models.PositiveIntegerField(default=1)
    max_day_duration = models.PositiveIntegerField(default=31)
    self_rental = models.ForeignKey('SelfRental', on_delete=models.CASCADE)

