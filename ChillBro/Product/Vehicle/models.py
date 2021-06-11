from django.core.validators import MinLengthValidator
from django.db import models
from .validations import validate_vehicle_registration_no


class Vehicle(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, related_name="vehicle", verbose_name="Product")
    vehicle_type = models.ForeignKey("VehicleType", on_delete=models.CASCADE, verbose_name="VehicleType")
    registration_no = models.CharField(max_length=15, validators=[MinLengthValidator(8),
                                                                  validate_vehicle_registration_no])

    def __str__(self):
        return "Product: {0}".format(self.product.name)
