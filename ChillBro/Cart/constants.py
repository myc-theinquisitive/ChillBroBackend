import enum

from ChillBro.constants import EntityType


class TripType(enum.Enum):
    round = "ROUND"
    single = "SINGLE"


class ProductTypes(enum.Enum):
    Hotel = "HOTEL"
    Rental = "RENTAL"
    Driver = "DRIVER"
    Vehicle = "VEHICLE"
    Hire_A_Vehicle = "HIRE_A_VEHICLE"
    Travel_Package_Vehicle = "TRAVEL_PACKAGE_VEHICLE"
    Self_Rental = "SELF_RENTAL"