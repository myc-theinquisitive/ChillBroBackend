from Product.product_interface import ProductInterface
from .serializers import HireAVehicleSerializer
from typing import Dict
from collections import defaultdict
from .models import HireAVehicle
from .wrapper import get_vehicle_type_data_by_id, get_vehicle_type_id_wise_details


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

        hire_a_vehicle_data_valid = self.hire_a_vehicle_serializer.is_valid()
        if not hire_a_vehicle_data_valid:
            is_valid = False
            errors.update(self.hire_a_vehicle_serializer.errors)

        return is_valid, errors

    def create(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle_type": string,
            "registration_no": string,
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
            "vehicle_type": string,
            "registration_no": string,
            "default_driver": string
        }
        """

        self.hire_a_vehicle_serializer.update(self.hire_a_vehicle_object, hire_a_vehicle_data)

    def get(self, product_id):
        self.hire_a_vehicle_object = HireAVehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        hire_a_vehicle_data = self.hire_a_vehicle_serializer.data
        vehicle_type_data = get_vehicle_type_data_by_id(hire_a_vehicle_data["vehicle_type"])
        hire_a_vehicle_data["vehicle_type"] = vehicle_type_data
        return hire_a_vehicle_data

    def get_by_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)

        hire_a_vehicle_serializer = HireAVehicleSerializer(hire_a_vehicles, many=True)
        hire_a_vehicles_data = hire_a_vehicle_serializer.data

        vehicle_type_ids = []
        for hire_a_vehicle_data in hire_a_vehicles_data:
            vehicle_type_ids.append(hire_a_vehicle_data["vehicle_type"])

        vehicle_type_id_wise_details = get_vehicle_type_id_wise_details(vehicle_type_ids)
        for hire_a_vehicle_data in hire_a_vehicles_data:
            hire_a_vehicle_data["vehicle_type"] = vehicle_type_id_wise_details[hire_a_vehicle_data["vehicle_type"]]

        return hire_a_vehicles_data
