from django.db import models
from ..BaseProduct.models import Product


class Amenities(models.Model):
    name = models.CharField(max_length=40)

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

    def __str__(self):
        return "Product: {0}".format(self.product.name)
