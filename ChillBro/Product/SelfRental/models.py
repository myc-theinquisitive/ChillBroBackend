from django.db import models
import uuid


def get_id():
    return str(uuid.uuid4())


class SelfRental(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="self_rental_product",
                                verbose_name="Vehicle")

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class DistancePrice(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    km_limit = models.PositiveIntegerField()
    excess_price = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    is_infinity = models.BooleanField(default=False)
    self_rental = models.ForeignKey('SelfRental', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('self_rental', 'km_limit')
