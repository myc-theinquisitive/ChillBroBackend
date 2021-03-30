from django.contrib import admin
from .models import RentBooking


@admin.register(RentBooking)
class RentalBookingAdmin(admin.ModelAdmin):
    pass
