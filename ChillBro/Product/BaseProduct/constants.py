import enum


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Rental = "RENTAL"
    Driver = "DRIVER"
    Vehicle = "VEHICLE"
    Hire_A_Vehicle = "HIRE_A_VEHICLE"
    Travel_Package_Vehicle = "TRAVEL_PACKAGE_VEHICLE"
    Travel_Agency = "TRAVEL_AGENCY"
    Make_Your_Own_Trip = "MAKE_YOUR_OWN_TRIP"
    Self_Rental = "SELF_RENTAL"


class ActivationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    YET_TO_VERIFY = "YET_TO_VERIFY"
    REJECTED = "REJECTED"
    DELETED = "DELETED"


class PriceTypes(enum.Enum):
    DAY = "DAY"
    HOUR = "HOUR"
    MONTH = "MONTH"
