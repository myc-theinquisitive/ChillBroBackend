from django.urls import re_path
from Bookings.consumers import BookingInstanceConsumer


websocket_urlpatterns = [
    re_path(r"^ws/booking/instance/$", BookingInstanceConsumer.as_asgi()),
]
