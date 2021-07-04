from django.db import models
from django.core.validators import MinValueValidator
import uuid
from .helpers import image_upload_to_travel_agency, upload_image_to_travel_characteristics
from .validations import is_json
from .constants import PlaceTypes


def get_id():
    return str(uuid.uuid4())


class TravelCharacteristics(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_url = models.ImageField(upload_to=upload_image_to_travel_characteristics, max_length=300)

    def __str__(self):
        return self.name


class TravelAgency(models.Model):
    product = models.OneToOneField("Product", on_delete=models.CASCADE, verbose_name="Product")
    duration_in_days = models.PositiveIntegerField(verbose_name="Duration in days",
                                                   validators=[MinValueValidator(0)])
    duration_in_nights = models.PositiveIntegerField(verbose_name="Duration in nights",
                                                     validators=[MinValueValidator(0)])
    tags = models.TextField(validators=[is_json])

    def __str__(self):
        return "Travel Agency: {0}".format(self.product.name)


class TravelAgencyPlaces(models.Model):
    travel_agency = models.ForeignKey("TravelAgency", on_delete=models.CASCADE, verbose_name="Travel Agency")
    type = models.CharField(max_length=20, choices=[(type.name, type.value) for type in PlaceTypes])
    place = models.ForeignKey("Place", on_delete=models.CASCADE, verbose_name="Agency Place")
    day_number = models.IntegerField(verbose_name='Day Number')
    order = models.IntegerField()

    class Meta:
        unique_together = ('travel_agency', 'place', 'order',)

    def __str__(self):
        return "Agency Place - {0}, {1}".format(self.travel_agency.product.name, self.place.name)


class TravelAgencyImage(models.Model):
    travel_agency = models.ForeignKey("TravelAgency", on_delete=models.CASCADE, verbose_name="Travel Agency")
    image = models.ImageField(upload_to=image_upload_to_travel_agency)
    order = models.IntegerField()

    class Meta:
        unique_together = ('travel_agency', 'order',)
        ordering = ['order']

    def __str__(self):
        return "Travel Agency Image - {0}".format(self.id)


class TravelAgencyCharacteristics(models.Model):
    travel_agency = models.ForeignKey("TravelAgency", on_delete=models.CASCADE)
    travel_characteristics = models.ForeignKey("TravelCharacteristics", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("travel_agency", "travel_characteristics")
