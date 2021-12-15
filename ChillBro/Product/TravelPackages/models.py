from django.db import models
from django.core.validators import MinValueValidator
import uuid
from .constants import Cities
from ChillBro.helpers import get_storage
from .helpers import image_upload_to_travel_package
from .validations import is_json


def get_id():
    return str(uuid.uuid4())


class TravelPackage(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    duration_in_days = models.PositiveIntegerField(verbose_name="Duration in days",
                                                   validators=[MinValueValidator(0)])
    duration_in_nights = models.PositiveIntegerField(verbose_name="Duration in nights",
                                                     validators=[MinValueValidator(0)])
    starting_point = models.CharField(max_length=36, choices=[(city.value, city.value) for city in Cities])
    tags = models.TextField(validators=[is_json])

    def __str__(self):
        return "Travel Package: {0}".format(self.name)


class PackagePlaces(models.Model):
    travel_package = models.ForeignKey("TravelPackage", on_delete=models.CASCADE, verbose_name="Travel Package")
    place = models.ForeignKey("Place", on_delete=models.CASCADE, verbose_name="Package Place")
    order = models.IntegerField()
    in_return = models.BooleanField(default=False)
    duration_to_reach = models.IntegerField()
    spending_time = models.IntegerField()

    class Meta:
        unique_together = ('travel_package', 'place', 'order',)
        ordering = ('order',)

    def __str__(self):
        return "Package Place - {0}, {1}".format(self.travel_package.name, self.place.name)


class TravelPackageImage(models.Model):
    travel_package = models.ForeignKey("TravelPackage", on_delete=models.CASCADE, verbose_name="Travel Package")
    image = models.ImageField(upload_to=image_upload_to_travel_package, storage=get_storage())
    order = models.IntegerField()

    class Meta:
        unique_together = ('travel_package', 'order',)
        ordering = ['order']

    def __str__(self):
        return "Travel Package Image - {0}".format(self.id)
