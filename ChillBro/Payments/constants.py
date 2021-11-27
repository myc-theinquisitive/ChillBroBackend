import enum
from ChillBro.constants import EntityType


class PayMode(enum.Enum):
    not_done = "NOT_DONE"
    upi = "UPI"
    cod = "COD"
    card = "CARD"


class PayStatus(enum.Enum):
    pending = "PENDING"
    done = "DONE"
    cancelled = "CANCELLED"
    failed = "FAILED"


class PaymentUser(enum.Enum):
    entity = "ENTITY"
    myc = "MYC"
    customer = "CUSTOMER"
