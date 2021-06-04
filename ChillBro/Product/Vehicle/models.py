from django.core.validators import MinValueValidator
from django.db import models
import uuid
from .helpers import upload_image_to_vehicle_type, upload_image_to_vehicle_characteristics
from .constants import WheelType


def get_id():
    return str(uuid.uuid4())


class VehicleCharacteristics(models.Model):
    name = models.CharField(max_length=100)
    icon_url = models.ImageField(upload_to=upload_image_to_vehicle_characteristics, max_length=300)
    units = models.CharField(max_length=30, null=True, blank=True)
    display_front = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    no_of_people = models.IntegerField(default=1,  validators=[MinValueValidator(1)])

    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    category_product = models.ForeignKey('CategoryProduct', on_delete=models.CASCADE, verbose_name="Category Product")
    wheel_type = models.CharField(
        max_length=30, choices=[(wheel_type.value, wheel_type.value) for wheel_type in WheelType])

    image = models.ImageField(upload_to=upload_image_to_vehicle_type, max_length=300)

    def __str__(self):
        return self.name + "-" + self.category.name


class VehicleTypeCharacteristics(models.Model):
    vehicle_type = models.ForeignKey("VehicleType", on_delete=models.CASCADE, verbose_name="Vehicle Type")
    vehicle_characteristic = models.ForeignKey("VehicleCharacteristics", on_delete=models.CASCADE,
                                               verbose_name="Vehicle Characteristic")
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.vehicle_type.name + "-" + self.vehicle_characteristic.name + "-" + self.value
