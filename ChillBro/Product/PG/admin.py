from django.contrib import admin
from .models import Amenities, HotelAvailableAmenities, HotelRoom


@admin.register(Amenities)
class AmenitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(HotelAvailableAmenities)
class HotelAvailableAmenitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    pass
