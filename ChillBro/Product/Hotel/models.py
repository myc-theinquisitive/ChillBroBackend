from django.core.validators import MinValueValidator
from django.db import models
from ..BaseProduct.models import Product
from .helpers import image_upload_to_amenities


class Amenities(models.Model):
    name = models.CharField(max_length=40)
    icon_url = models.ImageField(upload_to=image_upload_to_amenities)

    def __str__(self):
        return self.name


class HotelAvailableAmenities(models.Model):
    hotel_room = models.ForeignKey('HotelRoom', on_delete=models.CASCADE, verbose_name="Hotel")
    amenity = models.ForeignKey("Amenities", on_delete=models.CASCADE, verbose_name="Amenities")
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('hotel_room', 'amenity',)

    def __str__(self):
        return "Hotel Room: {0}, Amenities: {1}, Is Available {2}"\
            .format(self.hotel_room_id, self.amenity.name, self.is_available)


class HotelRoom(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, verbose_name="Product")
    max_no_of_people = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return "Product: {0}".format(self.product.name)
