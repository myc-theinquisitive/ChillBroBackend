import enum


class EntityType(enum.Enum):
    hotels = "HOTEL"
    transport = "TRANSPORT"
    rentals = "RENTAL"
    resorts = "RESORT"
    events = "EVENT"


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


class DateFilters(enum.Enum):
    today = "TODAY"
    yesterday = "YESTERDAY"
    week = "WEEK"
    month = "MONTH"
    total = "TOTAL"


class IdProofType(enum.Enum):
    aadhar_card = "AADHAR_CARD"
    pan_card = "PAN_CARD"
    voter_id = "VOTER_ID"


class PaymentUser(enum.Enum):
    entity = "ENTITY"
    myc = "MYC"
    customer = "CUSTOMER"
