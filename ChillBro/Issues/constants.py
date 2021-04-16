import enum


class Status(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


DEFAULT_FINAL_RESOLUTION = "Issue is not yet resolved"
