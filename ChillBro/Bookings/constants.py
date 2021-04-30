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


class ProductBookingStatus(enum.Enum):
    booked = "BOOKED"
    cancelled = "CANCELLED"


class DateFilters(enum.Enum):
    today = "TODAY"
    yesterday = "YESTERDAY"
    week = "WEEK"
    month = "MONTH"


class IdProofType(enum.Enum):
    aadhar_card = "AADHAR_CARD"
    pan_card = "PAN_CARD"
    voter_id = "VOTER_ID"

