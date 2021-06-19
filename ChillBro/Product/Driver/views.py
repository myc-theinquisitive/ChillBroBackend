from Product.product_interface import ProductInterface
from .serializers import DriverSerializer
from typing import Dict
from collections import defaultdict
from .models import Driver
from .wrapper import post_create_address, update_address_for_address_id, get_address_details_for_address_ids, \
    get_vehicle_type_data_by_id, get_vehicle_type_id_wise_details


def add_address_details_to_drivers(driver_list):
    address_ids = []
    for driver in driver_list:
        address_ids.append(driver["address_id"])

    addresses = get_address_details_for_address_ids(address_ids)
    address_per_address_id = defaultdict(dict)
    for address in addresses:
        address_per_address_id[address["id"]] = address

    for driver in driver_list:
        address_id = driver.pop("address_id", None)
        driver["address"] = address_per_address_id[address_id]


class DriverView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.driver_serializer = None
        self.driver_object = None

        self.address_data = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, driver_data):
        if driver_data:
            self.address_data = driver_data.pop("address", [])

        driver_object_defined = self.driver_object is not None
        driver_data_defined = driver_data is not None

        # for update
        if driver_object_defined and driver_data_defined:
            driver_data["address_id"] = self.driver_object.address_id
            self.driver_serializer = DriverSerializer(
                self.driver_object, data=driver_data)
        # for create
        elif driver_data_defined:
            # temp data for validation
            driver_data["address_id"] = "Yet To ADD"
            self.driver_serializer = DriverSerializer(data=driver_data)
        # for get
        elif driver_object_defined:
            self.driver_serializer = DriverSerializer(self.driver_object)
        else:
            self.driver_serializer = DriverSerializer()

    def validate_create_data(self, driver_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(driver_data)

        driver_data_valid = self.driver_serializer.is_valid()
        if not driver_data_valid:
            is_valid = False
            errors.update(self.driver_serializer.errors)

        # Creating address here to validate
        # This should be the last validation
        address_details = post_create_address(self.address_data)
        if not address_details['is_valid']:
            is_valid = False
            errors["address"] = address_details['errors']
        else:
            self.address_data["id"] = address_details['address_id']

        return is_valid, errors

    def create(self, driver_data):
        """
        driver: {
            "product_id": string, # internal data need not be validated
            "preferred_vehicle": string,
            "address": {
                "phone_number": 9999999999,
                "pincode": "533122",
                "city": "VSKP",
                "state": "AP",
                "country": "IND",

                "name": null,
                "address_line": null,
                "extend_address": null,
                "landmark": null,
                "latitude": null,
                "longitude": null
            },
            "licensed_from": YYYY
        }
        """
        driver_data["address_id"] = self.address_data["id"]
        driver_object = self.driver_serializer.create(driver_data)

        return {
            "id": driver_object.id
        }

    def validate_update_data(self, driver_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.driver_object \
                = Driver.objects.get(product_id=driver_data["product"])
        except Driver.DoesNotExist:
            return False, {"errors": "Driver does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(driver_data)

        driver_data_valid = self.driver_serializer.is_valid()
        if not driver_data_valid:
            is_valid = False
            errors.update(self.driver_serializer.errors)

        address_details = update_address_for_address_id(self.driver_object.address_id, self.address_data)
        if not address_details['is_valid']:
            is_valid = False
            errors["address"] = address_details['errors']
        return is_valid, errors

    def update(self, driver_data):
        """
        driver: {
            "product_id": string, # internal data need not be validated
            "preferred_vehicle": string,
            "address": {
                "phone_number": 9999999999,
                "pincode": "533122",
                "city": "VSKP",
                "state": "AP",
                "country": "IND",

                "name": null,
                "address_line": null,
                "extend_address": null,
                "landmark": null,
                "latitude": null,
                "longitude": null
            },
            "licensed_from": YYYY
        }
        """

        self.driver_serializer.update(self.driver_object, driver_data)

    def get(self, product_id):
        self.driver_object = Driver.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        driver_data = self.driver_serializer.data
        vehicle_type_data = get_vehicle_type_data_by_id(driver_data["preferred_vehicle"])
        driver_data["preferred_vehicle"] = vehicle_type_data
        add_address_details_to_drivers([driver_data])
        return driver_data

    def get_by_ids(self, product_ids):
        drivers = Driver.objects.filter(product_id__in=product_ids)
        driver_serializer = DriverSerializer(drivers, many=True)

        drivers_data = driver_serializer.data
        vehicle_type_ids = []
        for driver_data in drivers_data:
            vehicle_type_ids.append(driver_data["preferred_vehicle"])

        vehicle_type_id_wise_details = get_vehicle_type_id_wise_details(vehicle_type_ids)
        for driver_data in drivers_data:
            driver_data["preferred_vehicle"] = vehicle_type_id_wise_details[driver_data["preferred_vehicle"]]

        add_address_details_to_drivers(drivers_data)
        return drivers_data

    def get_sub_products_ids(self, product_ids):
        return {}, {}

    def get_transport_price_data(self, product_ids, product_ids_with_duration):
        return {}
