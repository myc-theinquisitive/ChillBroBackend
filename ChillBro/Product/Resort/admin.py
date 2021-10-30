from django.contrib import admin
from .models import ResortAvailableAmenities, ResortRoom, ResortAmenities


@admin.register(ResortAmenities)
class ResortAmenitiesAdmin(admin.ModelAdmin):
    pass

@admin.register(ResortAvailableAmenities)
class ResortAvailableAmenitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(ResortRoom)
class ResortRoomAdmin(admin.ModelAdmin):
    pass
