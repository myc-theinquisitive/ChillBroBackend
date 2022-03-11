from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Carousel)
admin.site.register(CarouselItem)
admin.site.register(BusinessClientFAQ)
admin.site.register(HelpCenterFAQ)
admin.site.register(HowToUse)
