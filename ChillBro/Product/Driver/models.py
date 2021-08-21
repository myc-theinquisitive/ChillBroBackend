from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import datetime


class Driver(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    preferred_vehicle = models.ForeignKey("VehicleType", on_delete=models.CASCADE,
                                          related_name="driver_preferred_vehicle", verbose_name="Vehicle")

    address_id = models.CharField(max_length=36)
    licensed_from = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.now().year)],
        help_text="Use the following format: <YYYY>")

    def __str__(self):
        return "Product: {0}".format(self.product.name)


class VehiclesDrivenByDriver(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Product")
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
