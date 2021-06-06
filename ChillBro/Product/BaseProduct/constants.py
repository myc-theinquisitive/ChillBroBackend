import enum


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Rental = "RENTAL"
    Driver = "DRIVER"
    Vehicle = "VEHICLE"
    Hire_A_Vehicle = "HIRE_A_VEHICLE"


class ActivationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    YET_TO_VERIFY = "YET_TO_VERIFY"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


class PriceTypes(enum.Enum):
    DAY = "DAY"
    HOUR = "HOUR"
    MONTH = "MONTH"
