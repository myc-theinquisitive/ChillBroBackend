from Product.product_interface import ProductInterface
from .serializers import VehicleSerializer
from typing import Dict
from collections import defaultdict
from .models import Vehicle
from .wrapper import get_vehicle_type_data_by_id, get_vehicle_type_id_wise_details


class VehicleView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.vehicle_serializer = None
        self.vehicle_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, vehicle_data):
        vehicle_object_defined = self.vehicle_object is not None
        vehicle_data_defined = vehicle_data is not None

        # for update
        if vehicle_object_defined and vehicle_data_defined:
            self.vehicle_serializer = VehicleSerializer(self.vehicle_object, data=vehicle_data)
        # for create
        elif vehicle_data_defined:
            self.vehicle_serializer = VehicleSerializer(data=vehicle_data)
        # for get
        elif vehicle_object_defined:
            self.vehicle_serializer = VehicleSerializer(self.vehicle_object)
        else:
            self.vehicle_serializer = VehicleSerializer()

    def validate_create_data(self, vehicle_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(vehicle_data)

        vehicle_data_valid = self.vehicle_serializer.is_valid()
        if not vehicle_data_valid:
            is_valid = False
            errors.update(self.vehicle_serializer.errors)

        return is_valid, errors

    def create(self, vehicle_data):
        """
        vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle_type": string,
            "registration_no": string,
        }
        """

        vehicle_object = self.vehicle_serializer.create(vehicle_data)

        return {
            "id": vehicle_object.id
        }

    def validate_update_data(self, vehicle_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.vehicle_object \
                = Vehicle.objects.get(product_id=vehicle_data["product"])
        except Vehicle.DoesNotExist:
            return False, {"errors": "Vehicle does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(vehicle_data)

        vehicle_data_valid = self.vehicle_serializer.is_valid()
        if not vehicle_data_valid:
            is_valid = False
            errors.update(self.vehicle_serializer.errors)

        return is_valid, errors

    def update(self, vehicle_data):
        """
        vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle_type": string,
            "registration_no": string,
        }
        """

        self.vehicle_serializer.update(self.vehicle_object, vehicle_data)

    def get(self, product_id):
        self.vehicle_object = Vehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        vehicle_data = self.vehicle_serializer.data
        vehicle_type_data = get_vehicle_type_data_by_id(vehicle_data["vehicle_type"])
        vehicle_data["vehicle_type"] = vehicle_type_data
        return vehicle_data

    def get_by_ids(self, product_ids):
        vehicles = Vehicle.objects.filter(product_id__in=product_ids)

        vehicle_serializer = VehicleSerializer(vehicles, many=True)
        vehicles_data = vehicle_serializer.data

        vehicle_type_ids = []
        for vehicle_data in vehicles_data:
            vehicle_type_ids.append(vehicle_data["vehicle_type"])

        vehicle_type_id_wise_details = get_vehicle_type_id_wise_details(vehicle_type_ids)
        for vehicle_data in vehicles_data:
            vehicle_data["vehicle_type"] = vehicle_type_id_wise_details[vehicle_data["vehicle_type"]]

        return vehicles_data

    def get_sub_products_ids(self, product_ids):
        return {}, {}

    def get_transport_price_data(self, product_ids, product_ids_with_duration):
        return {}
