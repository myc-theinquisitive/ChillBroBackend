import enum


class Status(enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class EntityTypes(enum.Enum):
    HOTEL = "HOTEL"
    TRANSPORT = "TRANSPORT"
    RENTAL = "RENTAL"


class VerifiedStatus(enum.Enum):
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    YET_TO_VERIFY = "YET_TO_VERIFY"
