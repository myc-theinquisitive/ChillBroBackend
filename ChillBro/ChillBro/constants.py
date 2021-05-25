import enum


class EntityType(enum.Enum):
    HOTEL = "HOTEL"
    TRANSPORT = "TRANSPORT"
    RENTAL = "RENTAL"
    EVENT = "EVENT"


class DateFilters(enum.Enum):
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    TOTAL = "TOTAL"
