from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import Bookings.routing
import Notifications.routing


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            Bookings.routing.websocket_urlpatterns +
            Notifications.routing.websocket_urlpatterns
        )
    )
})
