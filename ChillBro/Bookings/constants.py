import enum
from ChillBro.constants import EntityType, DateFilters, ProductTypes, TripType, DurationType, \
    COMMISION_FEE_PERCENT, TRANSACTION_FEE_PERCENT, FIXED_FEE_PERCENT, GST_PERCENT, PriceTypes


class BookingStatus(enum.Enum):
    yet_to_approve = "YET_TO_APPROVE"
    business_client_rejected = "BUSINESS_CLIENT_REJECTED"
    business_client_not_acted = "BUSINESS_CLIENT_NOT_ACTED"
    pending = "PENDING"
    ongoing = "ONGOING"
    cancelled = "CANCELLED"
    done = "DONE"


class PaymentStatus(enum.Enum):
    pending = "PENDING"
    failed = "FAILED"
    done = "DONE"
    not_required = "NOT_REQUIRED"


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


class PaymentMode(enum.Enum):
    partial = "PARTIAL"
    full = "FULL"


BookingApprovalTime = 10


