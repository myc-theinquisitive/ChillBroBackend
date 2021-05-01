import enum


class PayMode(enum.Enum):
    not_done = "NOT_DONE"
    upi = "UPI"
    cod = "COD"
    card = "CARD"


class EntityType(enum.Enum):
    hotels = "HOTELS"
    transport = "TRANSPORT"
    rentals = "RENTALS"
    resorts = "RESORTS"
    events = "EVENTS"


class PayStatus(enum.Enum):
    pending = "PENDING"
    done = "DONE"
    cancelled = "CANCELLED"


class PaymentUser(enum.Enum):
    entity = "ENTITY"
    myc = "MYC"
    customer = "CUSTOMER"
