from Product.product_interface import ProductInterface
from .serializers import HireAVehicleSerializer
from typing import Dict
from collections import defaultdict
from .models import HireAVehicle
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details, get_basic_driver_data_by_id, \
    get_basic_driver_id_wise_details, check_driver_exists_by_id, check_vehicle_exists_by_id


class HireAVehicleView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.hire_a_vehicle_serializer = None
        self.hire_a_vehicle_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, hire_a_vehicle_data):
        hire_a_vehicle_object_defined = self.hire_a_vehicle_object is not None
        hire_a_vehicle_data_defined = hire_a_vehicle_data is not None

        # for update
        if hire_a_vehicle_object_defined and hire_a_vehicle_data_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(
                self.hire_a_vehicle_object, data=hire_a_vehicle_data)
        # for create
        elif hire_a_vehicle_data_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(data=hire_a_vehicle_data)
        # for get
        elif hire_a_vehicle_object_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(self.hire_a_vehicle_object)
        else:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer()

    def validate_create_data(self, hire_a_vehicle_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(hire_a_vehicle_data)

        vehicle = hire_a_vehicle_data["vehicle"]
        default_driver = hire_a_vehicle_data["default_driver"]

        if not check_driver_exists_by_id(default_driver):
            is_valid = False
            errors['default_driver'] = "Default driver does not exist"

        if not check_vehicle_exists_by_id(vehicle):
            is_valid = False
            errors['vehicle'] = "Vehicle does not exist"
            return is_valid, errors

        hire_a_vehicle_data_valid = self.hire_a_vehicle_serializer.is_valid()
        if not hire_a_vehicle_data_valid:
            is_valid = False
            errors.update(self.hire_a_vehicle_serializer.errors)

        return is_valid, errors

    def create(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string
        }
        """

        hire_a_vehicle_object = self.hire_a_vehicle_serializer.create(hire_a_vehicle_data)

        return {
            "id": hire_a_vehicle_object.id
        }

    def validate_update_data(self, hire_a_vehicle_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.hire_a_vehicle_object \
                = HireAVehicle.objects.get(product_id=hire_a_vehicle_data["product"])
        except HireAVehicle.DoesNotExist:
            return False, {"errors": "Hotel A Vehicle does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(hire_a_vehicle_data)

        hire_a_vehicle_data_valid = self.hire_a_vehicle_serializer.is_valid()
        if not hire_a_vehicle_data_valid:
            is_valid = False
            errors.update(self.hire_a_vehicle_serializer.errors)

        return is_valid, errors

    def update(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string
        }
        """

        self.hire_a_vehicle_serializer.update(self.hire_a_vehicle_object, hire_a_vehicle_data)

    def get(self, product_id):
        self.hire_a_vehicle_object = HireAVehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        hire_a_vehicle_data = self.hire_a_vehicle_serializer.data
        vehicle_data = get_vehicle_data_by_id(hire_a_vehicle_data["vehicle"])
        hire_a_vehicle_data["vehicle"] = vehicle_data
        driver_data = get_basic_driver_data_by_id(hire_a_vehicle_data["default_driver"])
        hire_a_vehicle_data["default_driver"] = driver_data
        return hire_a_vehicle_data

    def get_by_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)

        hire_a_vehicle_serializer = HireAVehicleSerializer(hire_a_vehicles, many=True)
        hire_a_vehicles_data = hire_a_vehicle_serializer.data

        vehicle_ids = []
        for hire_a_vehicle_data in hire_a_vehicles_data:
            vehicle_ids.append(hire_a_vehicle_data["vehicle"])

        driver_ids = []
        for hire_a_vehicle_data in hire_a_vehicles_data:
            driver_ids.append(hire_a_vehicle_data["default_driver"])

        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        driver_id_wise_details = get_basic_driver_id_wise_details(driver_ids)
        for hire_a_vehicle_data in hire_a_vehicles_data:
            hire_a_vehicle_data["vehicle"] = vehicle_id_wise_details[hire_a_vehicle_data["vehicle"]]
            hire_a_vehicle_data["default_driver"] = driver_id_wise_details[hire_a_vehicle_data["default_driver"]]

        return hire_a_vehicles_data

    def get_sub_products_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_data = defaultdict(list)

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_data[each_hire_a_vehicle.product_id] = \
                [ each_hire_a_vehicle.vehicle_id, each_hire_a_vehicle.default_driver_id ]

        return hire_a_vehicles_data





