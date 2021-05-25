import enum


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Transport = "TRANSPORT"
    Rental = "RENTAL"


class ActivationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    YET_TO_VERIFY = "YET_TO_VERIFY"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


class PriceTypes(enum.Enum):
    DAY = "DAY"
    HOUR = "HOUR"
    MONTH = "MONTH"
