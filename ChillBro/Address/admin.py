from django.contrib import admin
from .models import Address, UserSavedAddress, Cities


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSavedAddress)
class UserSavedAddressAdmin(admin.ModelAdmin):
    pass


@admin.register(Cities)
class CitiesAdmin(admin.ModelAdmin):
    pass


