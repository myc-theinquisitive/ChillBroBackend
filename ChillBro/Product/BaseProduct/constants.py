import enum
from ChillBro.constants import PriceTypes


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
    Paid_Amenities = "PAID_AMENITIES"
    Event = "EVENT"
    PG = "PG"
    DORMITORY = "DORMITORY"
    RESORT = "RESORT"


class ActivationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    YET_TO_VERIFY = "YET_TO_VERIFY"
    REJECTED = "REJECTED"
    DELETED = "DELETED"

