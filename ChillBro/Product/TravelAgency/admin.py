from django.contrib import admin
from .models import TravelAgencyCharacteristics, TravelAgencyImage, TravelAgencyPlaces, TravelAgency

admin.site.register(TravelAgencyPlaces)
admin.site.register(TravelAgency)
admin.site.register(TravelAgencyImage)
admin.site.register(TravelAgencyCharacteristics)