import enum
from ChillBro.constants import EntityType, EntitySubType, DateFilters, ProductTypes, TripType, DurationType, \
    COMMISION_FEE_PERCENT, TRANSACTION_FEE_PERCENT, FIXED_FEE_PERCENT, GST_PERCENT, PriceTypes


class BookingStatus(enum.Enum):
    YET_TO_APPROVE = "YET_TO_APPROVE"
    BC_REJECTED = "BUSINESS_CLIENT_REJECTED"
    BC_NOT_ACTED = "BUSINESS_CLIENT_NOT_ACTED"
    PENDING = "PENDING"
    ONGOING = "ONGOING"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

    @classmethod
    def after_booking_confirmation_enums(cls):
        return [cls.PENDING.value, cls.ONGOING.value, cls.CANCELLED.value, cls.COMPLETED.value]


class PaymentStatus(enum.Enum):
    PENDING = "PENDING"
    FAILED = "FAILED"
    DONE = "DONE"
    NOT_REQUIRED = "NOT_REQUIRED"


class ProductBookingStatus(enum.Enum):
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"


class IdProofType(enum.Enum):
    AADHAR_CARD = "AADHAR_CARD"
    PAN_CARD = "PAN_CARD"
    VOTER_ID = "VOTER_ID"


class PaymentUser(enum.Enum):
    ENTITY = "ENTITY"
    MYC = "MYC"
    CUSTOMER = "CUSTOMER"


class PaymentMode(enum.Enum):
    PARTIAL = "PARTIAL"
    FULL = "FULL"


# in minutes
BookingApprovalTime = 10
