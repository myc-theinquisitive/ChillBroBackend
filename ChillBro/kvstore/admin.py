from django.contrib import admin
from .admin.admin import KVStoreAdminApp
from .models import Tag

# admin.site.register(Tag, KVStoreAdminApp)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
