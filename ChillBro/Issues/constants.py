import enum


class Status(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Departments(enum.Enum):
    CUSTOMER_CARE = "CUSTOMER_CARE"
    FINANCE = "FINANCE"


DEFAULT_FINAL_RESOLUTION = "Issue is not yet resolved"
USER_CLOSED_RESOLUTION = "Issue closed by user"
