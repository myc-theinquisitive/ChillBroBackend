from django.core.validators import MinLengthValidator
from django.db import models
from ..BaseProduct.models import Product
from ..Vehicle.models import VehicleType
from ..Vehicle.validations import validate_vehicle_registration_no


# TODO: price calculation per hour, per km details to be added??
class HireAVehicle(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name="Product")
    vehicle_type = models.OneToOneField(VehicleType, on_delete=models.CASCADE, verbose_name="VehicleType")
    registration_no = models.CharField(max_length=15, validators=[MinLengthValidator(8),
                                                                  validate_vehicle_registration_no])

    # TODO: make this foreign key to driver table
    default_driver = models.CharField(max_length=36)

    def __str__(self):
        return "Product: {0}".format(self.product.name)
