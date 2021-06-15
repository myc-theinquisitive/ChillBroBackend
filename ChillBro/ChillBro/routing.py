from django.urls import re_path
from ChillBro.Bookings.consumers import *


websocket_urlpatterns = [
    re_path(r"^ws/booking/instance/$", BookingInstanceConsumer.as_asgi()),
]
