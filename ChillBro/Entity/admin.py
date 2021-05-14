from django.contrib import admin
from .models import MyEntity, BusinessClientEntity, EntityAccount, EntityUPI, EntityVerification


admin.site.register(BusinessClientEntity)
admin.site.register(EntityAccount)
admin.site.register(EntityUPI)
admin.site.register(EntityVerification)


@admin.register(MyEntity)
class MyEntityAdmin(admin.ModelAdmin):
    pass
