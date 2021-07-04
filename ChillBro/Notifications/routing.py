from django.urls import re_path
from .consumers import NotificationCountConsumer


websocket_urlpatterns = [
    re_path(r"^ws/notifications/user/count/$", NotificationCountConsumer.as_asgi()),
]
