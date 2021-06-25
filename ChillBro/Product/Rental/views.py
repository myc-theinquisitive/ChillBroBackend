from collections import defaultdict

from .models import RentalProduct
from .serializers import RentalProductSerializer
from ..product_interface import ProductInterface
from typing import Dict


class RentalView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.rental_serializer = None
        self.rental_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, rental_data):

        rental_object_defined = self.rental_object is not None
        rental_data_defined = rental_data is not None

        # for update
        if rental_object_defined and rental_data_defined:
            self.rental_serializer = RentalProductSerializer(self.rental_object, data=rental_data)
        # for create
        elif rental_data_defined:
            self.rental_serializer = RentalProductSerializer(data=rental_data)
        # for get
        elif rental_object_defined:
            self.rental_serializer = RentalProductSerializer(self.rental_object)
        else:
            self.rental_serializer = RentalProductSerializer()

    def validate_create_data(self, rental_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(rental_data)

        rental_data_valid = self.rental_serializer.is_valid()
        if not rental_data_valid:
            is_valid = False
            errors.update(self.rental_serializer.errors)

        return is_valid, errors

    def create(self, rental_data):
        """
        rental_product: {
            "product_id": string, # internal data need not be validated
        }
        """

        rental_object = self.rental_serializer.create(rental_data)

        return {
            "id": rental_object.id
        }

    def validate_update_data(self, rental_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.rental_object \
                = RentalProduct.objects.get(product_id=rental_data["product"])
        except RentalProduct.DoesNotExist:
            return False, {"errors": "Rental Product does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(rental_data)

        rental_data_valid = self.rental_serializer.is_valid()
        if not rental_data_valid:
            is_valid = False
            errors.update(self.rental_serializer.errors)

        return is_valid, errors

    def update(self, rental_data):
        """
        rental_product: {
        }
        """

        self.rental_serializer.update(self.rental_object, rental_data)

    @staticmethod
    def update_rental_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.rental_object = RentalProduct.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        rental_data = self.rental_serializer.data
        rental_data = self.update_rental_response(rental_data)

        return rental_data

    def get_by_ids(self, product_ids):
        rental_products = RentalProduct.objects.filter(product_id__in=product_ids)

        rental_serializer = RentalProductSerializer(rental_products, many=True)
        rentals_data = rental_serializer.data

        for rental_data in rentals_data:
            rental_data = self.update_rental_response(rental_data)

        return rentals_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_ids_with_duration):
        return {}

    def calculate_final_prices(self, products):
        return {}

    def check_valid_duration(self, product_ids, start_time, end_time):
        is_valid = True
        errors = defaultdict(list)
        return is_valid, errors
