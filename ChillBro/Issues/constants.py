import enum


class Status(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


default_final_resolution = "Issue is not yet resolved"
