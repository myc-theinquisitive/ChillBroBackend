import enum
from ChillBro.constants import EntityType, DateFilters


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


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Rental = "RENTAL"
    Driver = "DRIVER"
    Vehicle = "VEHICLE"
    Hire_A_Vehicle = "HIRE_A_VEHICLE"
    Travel_Package_Vehicle = "TRAVEL_PACKAGE_VEHICLE"
    Self_Rental = "SELF_RENTAL"


class TripType(enum.Enum):
    round = "ROUND"
    single = "SINGLE"


class DurationType(enum.Enum):
    hour = "HOUR"
    day = "DAY"
    week = "WEEK"