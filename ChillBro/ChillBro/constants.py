import enum


class EntityType(enum.Enum):
    STAY = "STAY"
    TRANSPORT = "TRANSPORT"
    RENTAL = "RENTAL"
    EVENT = "EVENT"
    HIRE_A_VEHICLE = "HIRE_A_VEHICLE"


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
