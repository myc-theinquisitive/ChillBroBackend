from django.contrib import admin
from .models import MyEntity, BusinessClientEntity, EntityAccount, EntityUPI, EntityVerification, \
    Amenities, EntityAvailableAmenities, EntityImage


admin.site.register(BusinessClientEntity)
admin.site.register(EntityAccount)
admin.site.register(EntityUPI)
admin.site.register(EntityVerification)
admin.site.register(Amenities)
admin.site.register(EntityAvailableAmenities)
admin.site.register(EntityImage)


@admin.register(MyEntity)
class MyEntityAdmin(admin.ModelAdmin):
    pass
