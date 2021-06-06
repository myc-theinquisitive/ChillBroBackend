from django.contrib import admin
from .models import VehicleType, VehicleCharacteristics, VehicleTypeCharacteristics

admin.site.register(VehicleCharacteristics)
admin.site.register(VehicleType)
admin.site.register(VehicleTypeCharacteristics)
