import enum
from ChillBro.constants import EntityType, DateFilters


class BookingStatus(enum.Enum):
    yet_to_approve = "YET_TO_APPROVE"
    business_client_rejected = "BUSINESS_CLIENT_REJECTED"
    pending = "PENDING"
    ongoing = "ONGOING"
    cancelled = "CANCELLED"
    done = "DONE"


class PaymentStatus(enum.Enum):
    pending = "PENDING"
    failed = "FAILED"
    done = "DONE"
    not_required = "NOT_REQUIRED"


class PaymentMode(enum.Enum):
    cod = "COD"
    online = "ONLINE"


class ProductBookingStatus(enum.Enum):
    booked = "BOOKED"
    cancelled = "CANCELLED"


class IdProofType(enum.Enum):
    aadhar_card = "AADHAR_CARD"
    pan_card = "PAN_CARD"
    voter_id = "VOTER_ID"


class PaymentUser(enum.Enum):
    entity = "ENTITY"
    myc = "MYC"
    customer = "CUSTOMER"
