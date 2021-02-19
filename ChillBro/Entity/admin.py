from django.contrib import admin
from .models import MyEntity


@admin.register(MyEntity)
class MyEntityAdmin(admin.ModelAdmin):
    pass
