import enum


class Status(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class EntityTypes(enum.Enum):
    HOTEL = "HOTEL"
    TRANSPORT = "TRANSPORT"
    RENTAL = "RENTAL"


class Cities(enum.Enum):
    VSKP = "VISAKHAPATNAM"


class BankAccountTypes(enum.Enum):
    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    SALARY = "SALARY"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"


class ActivationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    YET_TO_VERIFY = "YET_TO_VERIFY"
    DELETED = "DELETED"
