from django.core.validators import MinValueValidator
from django.db import models

from ChillBro.helpers import get_storage
from ..BaseProduct.models import Product
from .helpers import image_upload_to_pg_amenities


class PGAmenities(models.Model):
    name = models.CharField(max_length=40)
    icon_url = models.ImageField(upload_to=image_upload_to_pg_amenities, storage=get_storage())

    def __str__(self):
        return self.name


class PGAvailableAmenities(models.Model):
    pg_room = models.ForeignKey('PGRoom', on_delete=models.CASCADE, verbose_name="PG")
    pg_amenity = models.ForeignKey("PGAmenities", on_delete=models.CASCADE, verbose_name="PG Amenities")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pg_room','pg_amenity')

    def __str__(self):
        return "PG Room: {0}, PG Amenities: {1}, Is Available {2}"\
            .format(self.pg_room_id, self.pg_amenity.name, self.is_available)


class PGRoom(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, verbose_name="Product")
    no_of_sharing = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return "Product: {0}".format(self.product.name)

