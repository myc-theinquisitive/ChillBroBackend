import enum
from ChillBro.constants import Cities, States, Countries


class JobType(enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"


class JobCategory(enum.Enum):
    SOFTWARE_DEVELOPMENT = "SOFTWARE_DEVELOPMENT"
    MARKETING_EXECUTIVE = "MARKETING_EXECUTIVE"


class JobApplicationStatus(enum.Enum):
    YET_TO_VIEW = "YET_TO_VIEW"
    VIEWED = "VIEWED"
    SHORT_LISTED = "SHORT_LISTED"
    REJECTED = "REJECTED"
