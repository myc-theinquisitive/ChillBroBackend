import enum


class EventMode(enum.Enum):
    online = "ONLINE"
    offline = "OFFLINE"
    online_offline = "ONLINE/OFFLINE"


class EventHostApp(enum.Enum):
    Zoom = "ZOOM"
    Teams = "MICROSOFT TEAMS"
    Meet = "GOOGLE MEET"


class EventPaymentType(enum.Enum):
    paid = "PAID"
    free = "FREE"
