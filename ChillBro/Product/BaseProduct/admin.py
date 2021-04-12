from django.contrib import admin
from .models import Product, ProductImage
from ..wrapper import get_key_value_taggable_inline


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [get_key_value_taggable_inline()]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass
