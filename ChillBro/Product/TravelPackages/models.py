from django.db import models
from django.core.validators import MinValueValidator
import uuid
from .helpers import image_upload_to_travel_package


def get_id():
    return str(uuid.uuid4())


class TravelPackage(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name="Category")
    category_product = models.ForeignKey('CategoryProduct', on_delete=models.CASCADE, verbose_name="Category Product")

    duration_in_days = models.PositiveIntegerField(verbose_name="Duration in days",
                                                   validators=[MinValueValidator(0)])
    duration_in_nights = models.PositiveIntegerField(verbose_name="Duration in nights",
                                                     validators=[MinValueValidator(0)])

    def __str__(self):
        return "Travel Package: {0}".format(self.name)


class PackagePlaces(models.Model):
    travel_package = models.ForeignKey("TravelPackage", on_delete=models.CASCADE, verbose_name="Travel Package")
    place = models.ForeignKey("Place", on_delete=models.CASCADE, verbose_name="Package Place")
    order = models.IntegerField()
    in_return = models.BooleanField(default=False)

    class Meta:
        unique_together = ('travel_package', 'place', 'order',)

    def __str__(self):
        return "Package Place - {0}, {1}".format(self.travel_package.name, self.place.name)


class TravelPackageImage(models.Model):
    travel_package = models.ForeignKey("TravelPackage", on_delete=models.CASCADE, verbose_name="Travel Package")
    image = models.ImageField(upload_to=image_upload_to_travel_package)
    order = models.IntegerField()

    class Meta:
        unique_together = ('travel_package', 'order',)
        ordering = ['order']

    def __str__(self):
        return "Travel Package Image - {0}".format(self.id)
