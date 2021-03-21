from django.contrib import admin
from .models import Category, CategoryImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(CategoryImage)
class CategoryImageAdmin(admin.ModelAdmin):
    pass
