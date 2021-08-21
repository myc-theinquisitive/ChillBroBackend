from django.contrib import admin
from .models import Events, EventSlots, EventPriceClasses

admin.site.register(Events)
admin.site.register(EventSlots)
admin.site.register(EventPriceClasses)
