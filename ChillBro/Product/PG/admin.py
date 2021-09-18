from django.contrib import admin
from .models import PGAvailableAmenities, PGRoom, PGAmenities


@admin.register(PGAmenities)
class PGAmenitiesAdmin(admin.ModelAdmin):
    pass

@admin.register(PGAvailableAmenities)
class PGAvailableAmenitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(PGRoom)
class PGRoomAdmin(admin.ModelAdmin):
    pass
