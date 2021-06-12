from Product.product_interface import ProductInterface
from .serializers import SelfRentalSerializer
from typing import Dict
from collections import defaultdict
from .models import SelfRental
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details

class SelfRentalView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.self_rental_serializer = None
        self.self_rental_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, self_rental_data):
        self_rental_object_defined = self.self_rental_object is not None
        self_rental_data_defined = self_rental_data is not None

        # for update
        if self_rental_object_defined and self_rental_data_defined:
            self.self_rental_serializer = SelfRentalSerializer(
                self.self_rental_object, data=self_rental_data)
        # for create
        elif self_rental_data_defined:
            self.self_rental_serializer = SelfRentalSerializer(data=self_rental_data)
        # for get
        elif self_rental_object_defined:
            self.self_rental_serializer = SelfRentalSerializer(self.self_rental_object)
        else:
            self.self_rental_serializer = SelfRentalSerializer()

    def validate_create_data(self, self_rental_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        print(self_rental_data,'this is my print')
        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        return is_valid, errors

    def create(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated
        }
        """

        self_rental_object = self.self_rental_serializer.create(self_rental_data)

        return {
            "id": self_rental_object.id
        }

    def validate_update_data(self, self_rental_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.self_rental_object \
                = SelfRental.objects.get(product_id=self_rental_data["product"])
        except SelfRental.DoesNotExist:
            return False, {"errors": "Hotel A Vehicle does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        return is_valid, errors

    def update(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated
        }
        """

        self.self_rental_serializer.update(self.self_rental_object, self_rental_data)

    def get(self, product_id):
        self.self_rental_object = SelfRental.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        self_rental_data = self.self_rental_serializer.data
        vehicle_data = get_vehicle_data_by_id(self_rental_data["product"])
        self_rental_data["product"] = vehicle_data
        return self_rental_data

    def get_by_ids(self, product_ids):
        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)

        self_rental_serializer = SelfRentalSerializer(self_rentals, many=True)
        self_rentals_data = self_rental_serializer.data

        vehicle_ids = []
        for self_rental_data in self_rentals_data:
            vehicle_ids.append(self_rental_data["product"])


        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        for self_rental_data in self_rentals_data:
            self_rental_data["vehicle"] = vehicle_id_wise_details[self_rental_data["vehicle"]]

        return self_rentals_data
