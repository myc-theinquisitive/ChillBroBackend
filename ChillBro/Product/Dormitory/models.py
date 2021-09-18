from django.core.validators import MinValueValidator
from django.db import models

from ChillBro.helpers import get_storage
from ..BaseProduct.models import Product
from .helpers import image_upload_to_dormitory_amenities


class DormitoryAmenities(models.Model):
    name = models.CharField(max_length=40)
    icon_url = models.ImageField(upload_to=image_upload_to_dormitory_amenities, storage=get_storage())

    def __str__(self):
        return self.name


class DormitoryAvailableAmenities(models.Model):
    dormitory_room = models.ForeignKey('DormitoryRoom', on_delete=models.CASCADE, verbose_name="Dormitory")
    dormitory_amenity = models.ForeignKey("DormitoryAmenities", on_delete=models.CASCADE, verbose_name="Dormitory Amenities")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('dormitory_room','dormitory_amenity')

    def __str__(self):
        return "Dormitory Room: {0}, Dormitory Amenities: {1}, Is Available {2}"\
            .format(self.dormitory_room_id, self.dormitory_amenity.name, self.is_available)


class DormitoryRoom(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, verbose_name="Product")

    def __str__(self):
        return "Product: {0}".format(self.product.name)

