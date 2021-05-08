from django.contrib import admin
from .models import MyEntity, BusinessClientEntity


admin.site.register(BusinessClientEntity)
@admin.register(MyEntity)
class MyEntityAdmin(admin.ModelAdmin):
    pass
