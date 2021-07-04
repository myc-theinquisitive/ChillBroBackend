import enum


class EntityType(enum.Enum):
    STAY = "STAY"
    TRANSPORT = "TRANSPORT"
    RENTAL = "RENTAL"
    EVENT = "EVENT"


class EntitySubType(enum.Enum):
    # for stay
    HOTEL = "HOTEL"
    RESORT = "RESORT"
    GUESTHOUSE = "GUESTHOUSE"

    DORMITORY_MEN = "DORMITORY_MEN"
    DORMITORY_WOMEN = "DORMITORY_WOMEN"
    DORMITORY_ALL = "DORMITORY_ALL"

    PG_MEN = "PG_MEN"
    PG_WOMEN = "PG_WOMEN"
    PG_ALL = "PG_ALL"


class DateFilters(enum.Enum):
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    TOTAL = "TOTAL"


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


class PriceTypes(enum.Enum):
    DAY = "DAY"
    HOUR = "HOUR"
    MONTH = "MONTH"
    PACKAGE = "PACKAGE"


COMMISION_FEE_PERCENT = 10
TRANSACTION_FEE_PERCENT = 2
FIXED_FEE_PERCENT = 2
GST_PERCENT = 18