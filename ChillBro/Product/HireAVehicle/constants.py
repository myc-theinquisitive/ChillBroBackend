import enum


class DurationType(enum.Enum):
    hour = "HOUR"
    day = "DAY"
    week = "WEEK"


class TripType(enum.Enum):
    round = "ROUND"
    single = "SINGLE"
