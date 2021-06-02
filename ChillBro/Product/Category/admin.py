from django.contrib import admin
from .models import Category, CategoryImage, CategoryProduct, CategoryProductPrices


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(CategoryProduct)
admin.site.register(CategoryProductPrices)
