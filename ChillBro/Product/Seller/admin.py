from django.contrib import admin
from .models import SellerProduct


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    pass

