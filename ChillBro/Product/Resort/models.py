from django.core.validators import MinValueValidator
from django.db import models

from ChillBro.helpers import get_storage
from ..BaseProduct.models import Product
from .helpers import image_upload_to_resort_amenities


class ResortAmenities(models.Model):
    name = models.CharField(max_length=40)
    icon_url = models.ImageField(upload_to=image_upload_to_resort_amenities, storage=get_storage())

    def __str__(self):
        return self.name


class ResortAvailableAmenities(models.Model):
    resort_room = models.ForeignKey('ResortRoom', on_delete=models.CASCADE, verbose_name="Resort")
    resort_amenity = models.ForeignKey("ResortAmenities", on_delete=models.CASCADE, verbose_name="Resort Amenities")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('resort_room','resort_amenity')

    def __str__(self):
        return "Resort Room: {0}, Resort Amenities: {1}, Is Available {2}"\
            .format(self.resort_room_id, self.resort_amenity.name, self.is_available)


class ResortRoom(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, verbose_name="Product")

    def __str__(self):
        return "Product: {0}".format(self.product.name)

