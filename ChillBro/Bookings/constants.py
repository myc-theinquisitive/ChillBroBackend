import enum


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
