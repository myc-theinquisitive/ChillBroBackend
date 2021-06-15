from Product.product_interface import ProductInterface
from .serializers import SelfRentalSerializer, DistancePriceSerializer
from typing import Dict
from collections import defaultdict
from .models import SelfRental, DistancePrice
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details, check_vehicle_exists_by_id


def check_distance_price_self_rental_by_id(distance_price_ids, self_rental_id):
    from .models import DistancePrice
    distance_price_objects = DistancePrice.objects.filter(id__in=distance_price_ids,
                                                          self_rental_id=self_rental_id).values_list('id')
    if len(list(distance_price_objects)) != len(distance_price_ids):
        invalid_ids = set(distance_price_ids) - set(distance_price_objects)
        return False, list(invalid_ids)
    return True, []


def get_distance_price_data(self_rental_id):
    distance_price = DistancePrice.objects.filter(self_rental_id=self_rental_id)

    distance_price_serializer = DistancePriceSerializer(distance_price, many=True)
    return distance_price_serializer.data


class SelfRentalView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.self_rental_serializer = None
        self.self_rental_object = None
        self.distance_price_data = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, self_rental_data):
        if self_rental_data:
            self.distance_price_data = self_rental_data.pop("distance_price", [])

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

        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        vehicle_data = check_vehicle_exists_by_id(self_rental_data['vehicle'])
        if not vehicle_data:
            is_valid = False
            errors['vehicle'] = "Vehicle does not exist"
            return is_valid, errors

        if vehicle_data['registration_type'] != "RENTAL":
            is_valid = False
            errors['registration_type'] = "Only Commercial Vehicle allowed"

        km_limit_list = list(map(lambda x: x['km_limit'], self.distance_price_data))
        if len(set(km_limit_list)) != len(km_limit_list):
            is_valid = False
            errors['km_limit'] = "KM limit values must be unique"

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        distance_price_serializer = DistancePriceSerializer(
            data=self.distance_price_data, many=True)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        return is_valid, errors

    def create(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated,
            "vehicle_id": string
            distance_price: [
                    {
                        'price': int,
                        'km_limit': int,
                        'excess_price':int,
                        'excess_price_per_hour': int,
                        is_infinity: Boolean
                    }
                ]
        }
        """

        self_rental_object = self.self_rental_serializer.create(self_rental_data)

        for distance_price in self.distance_price_data:
            distance_price["self_rental"] = self_rental_object
            if 'is_infinity' in distance_price:
                distance_price['excess_price'] = 0 if distance_price['is_infinity'] else distance_price['excess_price']
            else:
                distance_price['is_infinity'] = False

        distance_price_serializer = DistancePriceSerializer()

        distance_price_serializer.bulk_create(self.distance_price_data)

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
            return False, {"errors": "Self Rental does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        km_limit_list = list(map(lambda x: x['km_limit'], self.distance_price_data['add']))

        if len(set(km_limit_list)) != len(km_limit_list):
            is_valid = False
            errors['km_limit'] = "KM limit values must be unique"
            return is_valid, errors

        km_limit_errors = DistancePrice.objects.filter(self_rental_id=self.self_rental_object['id'],
                                                       km_limit__in=km_limit_list).values_list('km_limit')

        if len(km_limit_errors) > 0:
            is_valid = False
            errors['km_limit already exists'] = km_limit_errors

        distance_price_ids = list(
            map(lambda x: x['id'], self.distance_price_data['change'] + self.distance_price_data['delete']))
        invalid_distance_price_ids = check_distance_price_self_rental_by_id(distance_price_ids,
                                                                            self.self_rental_object['id'])
        if invalid_distance_price_ids[0]:
            is_valid = False
            errors["invalid distance_price id's"] = invalid_distance_price_ids[1]

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        distance_price_serializer = DistancePriceSerializer(data=self.distance_price_data)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors.update(distance_price_serializer.errors)
            return is_valid, errors
        return is_valid, errors

    def update(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "distance_price" :{
                "add": [
                    {
                        'price': int,
                        'km_limit': int,
                        'excess_price': int,
                        'excess_price_per_hour': int,
                    }
                ],
                "change": [
                    {
                        'id': string,
                        'price': int,
                        'km_limit': int,
                        'excess_price': int,
                        'excess_price_per_hour': int,
                   }
                ]
                "delete": [
                    {
                        'id': string
                    }
                ]
            }
        }
        """

        self.self_rental_serializer.update(self.self_rental_object, self_rental_data)
        distance_price_serializer = DistancePriceSerializer()
        distance_price_serializer.bulk_create(self.distance_price_data["add"])
        distance_price_serializer.bulk_update(self.distance_price_data["change"])
        distance_price_serializer.bulk_delete(self.distance_price_data["delete"])

    def get(self, product_id):
        self.self_rental_object = SelfRental.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        self_rental_data = self.self_rental_serializer.data
        vehicle_data = get_vehicle_data_by_id(self_rental_data["vehicle"])
        self_rental_data["distance_price"] = get_distance_price_data(self.self_rental_object.id)

        self_rental_data["vehicle"] = vehicle_data

        return self_rental_data

    def get_by_ids(self, product_ids):
        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)

        self_rental_serializer = SelfRentalSerializer(self_rentals, many=True)
        self_rentals_data = self_rental_serializer.data

        for self_rental in self_rentals_data:
            self_rental["distance_price"] = get_distance_price_data(self_rental['id'])

        vehicle_ids = []
        for self_rental_data in self_rentals_data:
            vehicle_ids.append(self_rental_data["vehicle"])

        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        for self_rental_data in self_rentals_data:
            self_rental_data["vehicle"] = vehicle_id_wise_details[self_rental_data["vehicle"]]

        return self_rentals_data
