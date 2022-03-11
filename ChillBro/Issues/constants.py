import enum
from ChillBro.constants import EntityType


class SupportStatus(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class UserStatus(enum.Enum):
    YET_TO_RECEIVE_CALL = "YET_TO_RECEIVE_CALL"
    CALL_RECEIVED = "CALL_RECEIVED"
    RESOLVED = "RESOLVED"


class Departments(enum.Enum):
    CUSTOMER_CARE = "CUSTOMER_CARE"
    FINANCE = "FINANCE"


DEFAULT_FINAL_RESOLUTION = "Issue is not yet resolved"
USER_CLOSED_RESOLUTION = "Issue closed by user"
