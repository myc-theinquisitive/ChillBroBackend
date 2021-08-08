from django.contrib import admin
from .models import Driver, VehiclesDrivenByDriver

admin.site.register(Driver)
admin.site.register(VehiclesDrivenByDriver)
