from django.contrib import admin
from .models import DormitoryAvailableAmenities, DormitoryRoom, DormitoryAmenities


@admin.register(DormitoryAmenities)
class DormitoryAmenitiesAdmin(admin.ModelAdmin):
    pass

@admin.register(DormitoryAvailableAmenities)
class DormitoryAvailableAmenitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(DormitoryRoom)
class DormitoryRoomAdmin(admin.ModelAdmin):
    pass
