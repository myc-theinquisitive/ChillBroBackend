from django.db import models
import uuid


def get_id():
    return str(uuid.uuid4())


# TODO: price calculation per hour, per km details to be added??
class SelfRental(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    vehicle = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="self_rental_product",
                                verbose_name="Vehicle")

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class DistancePrice(models.Model):
    price = models.IntegerField()
    km_limit = models.IntegerField()
    excess_price = models.IntegerField()
    is_infinity = models.BooleanField(default=False)
    self_rental = models.ForeignKey('SelfRental', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('self_rental', 'km_limit')
