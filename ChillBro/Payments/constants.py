import enum


class PayMode(enum.Enum):
    not_done = "NOT_DONE"
    upi = "UPI"
    cod = "COD"
    card = "CARD"


class EntityType(enum.Enum):
    hotels = "HOTEL"
    transport = "TRANSPORT"
    rentals = "RENTAL"
    resorts = "RESORT"
    events = "EVENT"


class PayStatus(enum.Enum):
    pending = "PENDING"
    done = "DONE"
    cancelled = "CANCELLED"


class PaymentUser(enum.Enum):
    entity = "ENTITY"
    myc = "MYC"
    customer = "CUSTOMER"
