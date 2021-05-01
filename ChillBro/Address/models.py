from django.db import models
from .constants import Countries, States, Cities
import uuid


def get_id():
    return str(uuid.uuid4())


class Address(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=get_id)
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Name")
    phone_number = models.CharField(max_length=10, blank=True, null=True, verbose_name="Phone Number")
    pincode = models.CharField(max_length=10, blank=True, null=True, verbose_name="Pincode")
    address_line = models.CharField(max_length=250, blank=True, null=True, verbose_name="Address Line")
    extend_address = models.CharField(max_length=250, blank=True, null=True, verbose_name="Extend Address")
    landmark = models.CharField(max_length=250, blank=True, null=True, verbose_name="Landmark")
    city = models.CharField(max_length=30, default=Cities.VSKP.value,
                            choices=[(city.name, city.value) for city in Cities], verbose_name="City")
    state = models.CharField(max_length=30, default=States.AP.value,
                             choices=[(state.name, state.value) for state in States], verbose_name="State")
    country = models.CharField(max_length=30, default=Countries.IND.value,
                               choices=[(country.name, country.value) for country in Countries], verbose_name="Country")
    latitude = models.CharField(max_length=15, blank=True, null=True, verbose_name="Latitude")
    longitude = models.CharField(max_length=15, blank=True, null=True, verbose_name="Longitude")

    def __str__(self):
        return "Address Nº{0}".format(self.id)

