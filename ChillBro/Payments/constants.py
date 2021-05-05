import enum


class PayMode(enum.Enum):
    upi = "UPI"
    cod = "COD"
    card = "CARD"


class EntityType(enum.Enum):
    hotels = "HOTELS"
    transport = "TRANSPORT"
    rentals = "RENTALS"
    resorts = "RESORTS"
    events = "EVENTS"


class BookingStatus(enum.Enum):
    pending = "PENDING"
    ongoing = "ONGOING"
    cancelled = "CANCELLED"
    done = "DONE"


class PayStatus(enum.Enum):
    pending = "PENDING"
    done = "DONE"