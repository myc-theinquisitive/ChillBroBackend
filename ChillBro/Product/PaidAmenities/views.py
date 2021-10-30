from Product.product_interface import ProductInterface
from .serializers import PaidAmenitiesSerializer
from typing import Dict
from collections import defaultdict
from .models import PaidAmenities


class PaidAmenitiesView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.paid_amenities_serializer = None
        self.paid_amenities_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, paid_amenities_data):

        paid_amenities_object_defined = self.paid_amenities_object is not None
        paid_amenities_data_defined = paid_amenities_data is not None

        # for update
        if paid_amenities_object_defined and paid_amenities_data_defined:
            self.paid_amenities_serializer = PaidAmenitiesSerializer(self.paid_amenities_object,
                                                                           data=paid_amenities_data)
        # for create
        elif paid_amenities_data_defined:
            self.paid_amenities_serializer = PaidAmenitiesSerializer(data=paid_amenities_data)
        # for get
        elif paid_amenities_object_defined:
            self.paid_amenities_serializer = PaidAmenitiesSerializer(self.paid_amenities_object)
        else:
            self.paid_amenities_serializer = PaidAmenitiesSerializer()

    def validate_create_data(self, paid_amenities_data: Dict) -> (bool, Dict):

        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(paid_amenities_data)

        paid_amenities_data_valid = self.paid_amenities_serializer.is_valid()
        if not paid_amenities_data_valid:
            is_valid = False
            errors.update(self.paid_amenities_serializer.errors)


        return is_valid, errors

    def create(self, paid_amenities_data):
        """
        paid_amenities: {
            "product_id": string, # internal data need not be validated
        }
        """

        paid_amenities_object = self.paid_amenities_serializer.create(paid_amenities_data)

        return {
            "id": paid_amenities_object.id
        }

    def validate_update_data(self, paid_amenities_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.paid_amenities_object \
                = PaidAmenities.objects.get(product_id=paid_amenities_data["product"])
        except PaidAmenities.DoesNotExist:
            return False, {"errors": "PaidAmenities does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(paid_amenities_data)

        paid_amenities_data_valid = self.paid_amenities_serializer.is_valid()
        if not paid_amenities_data_valid:
            is_valid = False
            errors.update(self.paid_amenities_serializer.errors)

        return is_valid, errors

    def update(self, paid_amenities_data):
        """
        paid_amenities: {
            "product_id": string, # internal data need not be validated
        }
        """

        self.paid_amenities_serializer.update(self.paid_amenities_object, paid_amenities_data)


    def get(self, product_id):
        self.paid_amenities_object = PaidAmenities.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        paid_amenities_data = self.paid_amenities_serializer.data

        return paid_amenities_data

    def get_by_ids(self, product_ids):
        paid_amenitiess = PaidAmenities.objects.filter(product_id__in=product_ids)

        paid_amenities_serializer = PaidAmenitiesSerializer(paid_amenitiess, many=True)
        paid_amenitiess_data = paid_amenities_serializer.data

        return paid_amenitiess_data
