from django.contrib import admin
from .models import Category, CategoryImage, CategoryPrices


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(CategoryPrices)