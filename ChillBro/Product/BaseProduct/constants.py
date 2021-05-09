import enum


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Transport = "TRANSPORT"
    Rental = "RENTAL"


class ProductStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    DELETED = "DELETED"
