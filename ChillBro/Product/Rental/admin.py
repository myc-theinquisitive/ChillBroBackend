from django.contrib import admin
from .models import RentalProduct


@admin.register(RentalProduct)
class RentalProductAdmin(admin.ModelAdmin):
    pass
