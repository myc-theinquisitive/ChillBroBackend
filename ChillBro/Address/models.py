from django.db import models
from .constants import Countries, States, Cities, AddressType
import uuid
from django.contrib.auth import get_user_model
from ChillBro.helpers import get_storage


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
    # TODO: should point to cities table
    city = models.CharField(max_length=30, default=Cities.VSKP.value,
                            choices=[(city.value, city.value) for city in Cities], verbose_name="City")
    state = models.CharField(max_length=30, default=States.AP.value,
                             choices=[(state.value, state.value) for state in States], verbose_name="State")
    country = models.CharField(max_length=30, default=Countries.IND.value,
                               choices=[(country.value, country.value) for country in Countries], verbose_name="Country")
    latitude = models.CharField(max_length=15, blank=True, null=True, verbose_name="Latitude")
    longitude = models.CharField(max_length=15, blank=True, null=True, verbose_name="Longitude")

    def __str__(self):
        return "Address Nº{0}".format(self.id)


class UserSavedAddress(models.Model):
    address = models.ForeignKey('Address', on_delete=models.CASCADE, verbose_name="Address")
    address_type = models.CharField(max_length=15, choices=[(address_type.value, address_type.value)
                                    for address_type in AddressType], default=AddressType.HOME.value)
    user_model = get_user_model()
    created_by = models.ForeignKey(user_model, on_delete=models.CASCADE, verbose_name="User")

    def __str__(self):
        return "User: {0}, Address Id: {1}".format(self.created_by, self.address_id)


class Cities(models.Model):
    from .helpers import upload_image_to_city_icon
    name = models.CharField(max_length=30, unique=True)
    short_name = models.CharField(max_length=30, unique=True)
    image_url = models.ImageField(upload_to=upload_image_to_city_icon, max_length=300, storage=get_storage())

    def __str__(self):
        return "Category - {0}".format(self.name)
