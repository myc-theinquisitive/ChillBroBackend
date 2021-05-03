import enum


class ProductTypes(enum.Enum):
    Hotel = "Hotel"
    Transport = "Transport"
    Rental = "Rental"


class ProductStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    DELETED = "DELETED"
