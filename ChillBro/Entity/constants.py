import enum
from ChillBro.constants import EntityType


class Status(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


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
