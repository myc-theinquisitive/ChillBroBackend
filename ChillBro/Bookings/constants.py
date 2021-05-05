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


class DateFilters(enum.Enum):
    today = "TODAY"
    yesterday = "YESTERDAY"
    week = "WEEK"
    month = "MONTH"


class IdProofType(enum.Enum):
    aadhar_card = "AADHAR_CARD"
    pan_card = "PAN_CARD"
    voter_id = "VOTER_ID"



