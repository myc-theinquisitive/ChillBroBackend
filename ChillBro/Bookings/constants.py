import enum


class Type(enum.Enum):
    Hotels = "Hotels"
    Transport = "Transport"
    Rentals = "Rentals"
    Resorts = "Resorts"
    Events = "Events"

class Status(enum.Enum):
    PENDING = "PENDING"
    ONGOING = "ONGOING"
    CANCELLED = "CANCELLED"
    DONE =  "DONE"

class Pay_status(enum.Enum):
    PENDING = "PENDING"
    DONE = "DONE"