from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Bookings)
admin.site.register(BookedProducts)
admin.site.register(BookedProductExtraDetails)
admin.site.register(CheckInDetails)
admin.site.register(CheckOutDetails)
admin.site.register(CancelledDetails)
admin.site.register(CheckInImages)
admin.site.register(CheckOutImages)
admin.site.register(BusinessClientReportOnCustomer)

