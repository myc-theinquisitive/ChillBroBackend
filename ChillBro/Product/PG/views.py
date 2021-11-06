from datetime import datetime
from math import ceil
from typing import List, Dict
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from Bookings.helpers import get_date_format
from ChillBro.constants import PriceTypes
from .models import PGAmenities, PGRoom, PGAvailableAmenities
from .serializers import PGAmenityIsAvailableSerializer, PGAvailableAmenitiesSerializer, PGRoomSerializer, \
    PGAvailableAmenitiesUpdateSerializer, PGAmenitiesSerializer
from ..BaseProduct.models import Product
from ..product_interface import ProductInterface
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsGet


def validate_pg_amenity_ids(pg_amenity_ids: List[int]) -> (bool, List[int]):
    existing_pg_amenities = PGAmenities.objects.filter(id__in=pg_amenity_ids).values_list('id', flat=True)
    if len(existing_pg_amenities) != len(pg_amenity_ids):
        return False, set(pg_amenity_ids) - set(existing_pg_amenities)
    return True, []


def validate_pg_ids(pg_ids: List[int]) -> (bool, List[int]):
    existing_pg_ids = PGRoom.objects.filter(id__in=pg_ids)\
        .values_list('id', flat=True)
    if len(existing_pg_ids) != len(pg_ids):
        return False, set(pg_ids) - set(existing_pg_ids)
    return True, []


def validate_pg_available_pg_amenities_ids(pg_room_id: int, pg_available_amenity_ids: List[int])\
        -> (bool, List[int]):
    existing_pg_available_amenity_ids \
        = PGAvailableAmenities.objects.filter(id__in=pg_available_amenity_ids, pg_room_id=pg_room_id)\
        .values_list('id', flat=True)
    if len(existing_pg_available_amenity_ids) != len(pg_available_amenity_ids):
        return False, set(pg_available_amenity_ids) - set(existing_pg_available_amenity_ids)
    return True, []


class PGAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet)
    queryset = PGAmenities.objects.all()
    serializer_class = PGAmenitiesSerializer


class PGAvailableAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PGAvailableAmenities.objects.all()
    serializer_class = PGAvailableAmenitiesSerializer


class PGAvailableAmenitiesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PGAvailableAmenities.objects.all()
    serializer_class = PGAvailableAmenitiesSerializer


class PGView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.pg_room_serializer = None
        self.pg_amenities_data = None

        self.pg_room_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, pg_room_data):
        if pg_room_data:
            self.pg_amenities_data = pg_room_data.pop("pg_amenities", None)

        pg_room_object_defined = self.pg_room_object is not None
        pg_room_data_defined = pg_room_data is not None

        # for update
        if pg_room_object_defined and pg_room_data_defined:
            self.pg_room_serializer = PGRoomSerializer(self.pg_room_object, data=pg_room_data)
        # for create
        elif pg_room_data_defined:
            self.pg_room_serializer = PGRoomSerializer(data=pg_room_data)
        # for get
        elif pg_room_object_defined:
            self.pg_room_serializer = PGRoomSerializer(self.pg_room_object)
        else:
            self.pg_room_serializer = PGRoomSerializer()

    def validate_create_data(self, pg_room_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(pg_room_data)

        pg_data_valid = self.pg_room_serializer.is_valid()
        if not pg_data_valid:
            is_valid = False
            errors.update(self.pg_room_serializer.errors)

        # Additional validations except serializer validations
        pg_amenity_ids = []
        for pg_amenity_dict in self.pg_amenities_data:
            if "pg_amenity" not in pg_amenity_dict:
                is_valid = False
                errors["pg_amenity"].append("This field is required.")
                continue
            if "is_available" not in pg_amenity_dict:
                is_valid = False
                errors["is_available"].append("This field is required.")
                continue
            pg_amenity_ids.append(pg_amenity_dict["pg_amenity"])

        pg_amenity_ids_valid, invalid_ids = validate_pg_amenity_ids(pg_amenity_ids)
        if not pg_amenity_ids_valid:
            is_valid = False
            errors["invalid_pg_amenity_ids"] = invalid_ids

        return is_valid, errors

    def create(self, pg_room_data):
        """
        pg_room: {
            "product_id": string, # internal data need not be validated
            "no_of_sharing": int,
            "pg_amenities": [
                {
                    "pg_amenity": string,
                    "is_available": boolean
                }
            ]
        }
        """

        pg_room_object = self.pg_room_serializer.create(pg_room_data)

        for pg_amenity in self.pg_amenities_data:
            pg_amenity["pg_room"] = pg_room_object.id

        pg_available_pg_amenities_serializer = PGAvailableAmenitiesSerializer()
        pg_available_pg_amenities_serializer.bulk_create(self.pg_amenities_data)

        return {
            "id": pg_room_object.id
        }

    def validate_update_data(self, pg_room_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.pg_room_object \
                = PGRoom.objects.get(product_id=pg_room_data["product"])
        except PGRoom.DoesNotExist:
            return False, {"errors": "PGRoom does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(pg_room_data)

        pg_data_valid = self.pg_room_serializer.is_valid()
        if not pg_data_valid:
            is_valid = False
            errors.update(self.pg_room_serializer.errors)

        pg_available_pg_amenities_update_serializer = PGAvailableAmenitiesUpdateSerializer(data=self.pg_amenities_data)
        pg_available_pg_amenities_update_data_valid = pg_available_pg_amenities_update_serializer.is_valid()

        if not pg_available_pg_amenities_update_data_valid:
            is_valid = False
            errors.update(pg_available_pg_amenities_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        pg_amenity_ids = []
        pg_available_amenity_ids = []
        for pg_amenity in self.pg_amenities_data["add"]:
            pg_available_pg_amenities_exists = PGAvailableAmenities.objects\
                .filter(pg_room=self.pg_room_object, pg_amenity_id=pg_amenity["pg_amenity"]).exists()
            if pg_available_pg_amenities_exists:
                is_valid = False
                errors["PGRoom-Amenity"].append("PGRoom-{0}, Amenity-{1}: Already Exists!"
                                                   .format(self.pg_room_object.id, pg_amenity["pg_amenity"]))

            pg_amenity["pg_room"] = self.pg_room_object.id
            pg_amenity_ids.append(pg_amenity["pg_amenity"])

        for pg_amenity in self.pg_amenities_data["change"]:
            pg_available_amenity_ids.append(pg_amenity["id"])

        for pg_amenity in self.pg_amenities_data["delete"]:
            pg_available_amenity_ids.append(pg_amenity["id"])

        pg_amenity_ids_valid, invalid_pg_amenity_ids = validate_pg_amenity_ids(pg_amenity_ids)
        if not pg_amenity_ids_valid:
            is_valid = False
            errors["invalid_pg_amenity_ids"] = invalid_pg_amenity_ids

        pg_available_pg_amenities_ids_valid, invalid_pg_available_pg_amenities_ids \
            = validate_pg_available_pg_amenities_ids(self.pg_room_object.id, pg_available_amenity_ids)
        if not pg_available_pg_amenities_ids_valid:
            is_valid = False
            errors["invalid_pg_available_pg_amenities_ids"] = invalid_pg_available_pg_amenities_ids

        return is_valid, errors

    def update(self, pg_room_data):
        """
        pg_room: {
            "product_id": string, # internal data need not be validated,
            "no_of_sharing": int,
            "pg_amenities": {
                "add": [
                    {
                        "pg_amenity": string,
                        "is_available": boolean
                    }
                ],
                "change": [
                    {
                        "id": string,
                        "is_available": boolean
                    }
                ],
                "delete": [
                    {
                        "id": string
                    }
                ]
            }
        }
        """

        self.pg_room_serializer.update(self.pg_room_object, pg_room_data)

        pg_available_pg_amenities_serializer = PGAvailableAmenitiesSerializer()
        pg_available_pg_amenities_serializer.bulk_create(self.pg_amenities_data["add"])
        pg_available_pg_amenities_serializer.bulk_update(self.pg_amenities_data["change"])
        pg_available_pg_amenities_serializer.bulk_delete(self.pg_amenities_data["delete"])

    @staticmethod
    def convert_available_pg_amenities_to_dict(available_pg_amenity):
        image_url = available_pg_amenity.pg_amenity.icon_url.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        return {
            "id": available_pg_amenity.id,
            "name": available_pg_amenity.pg_amenity.name,
            "icon_url": image_url,
            "is_available": available_pg_amenity.is_available
        }

    @staticmethod
    def update_pg_room_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.pg_room_object = PGRoom.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        pg_room_data = self.pg_room_serializer.data
        pg_room_data = self.update_pg_room_response(pg_room_data)

        available_pg_amenities = PGAvailableAmenities.objects.select_related('pg_amenity')\
            .filter(pg_room=self.pg_room_object)

        available_pg_amenities_data = []
        for available_pg_amenity in available_pg_amenities:
            available_pg_amenity_data = self.convert_available_pg_amenities_to_dict(available_pg_amenity)
            available_pg_amenities_data.append(available_pg_amenity_data)

        pg_room_data["available_pg_amenities"] = available_pg_amenities_data
        return pg_room_data

    def get_by_ids(self, product_ids):
        pg_rooms = PGRoom.objects.filter(product_id__in=product_ids)

        pg_rooms_serializer = PGRoomSerializer(pg_rooms, many=True)
        pg_rooms_data = pg_rooms_serializer.data

        pg_room_ids = []
        for pg_room_data in pg_rooms_data:
            pg_room_data = self.update_pg_room_response(pg_room_data)
            pg_room_ids.append(pg_room_data["id"])

        available_pg_amenities = PGAvailableAmenities.objects.select_related('pg_amenity') \
            .filter(pg_room__in=pg_room_ids)
        pg_room_wise_available_pg_amenities_dict = defaultdict(list)
        for available_pg_amenity in available_pg_amenities:
            available_pg_amenity_data = self.convert_available_pg_amenities_to_dict(available_pg_amenity)
            pg_room_wise_available_pg_amenities_dict[available_pg_amenity.pg_room_id].append(
                available_pg_amenity_data)

        for pg_room_data in pg_rooms_data:
            pg_room_data["available_pg_amenities"] = pg_room_wise_available_pg_amenities_dict[pg_room_data["id"]]

        return pg_rooms_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        products = Product.objects.filter(id__in=product_ids)
        starting_prices = defaultdict()
        for each_product in products:
            each_pg_details = product_details_with_ids[each_product.product_id]
            start_time_date_object = each_pg_details['start_time']
            end_time_date_object = each_pg_details['end_time']
            quantity = each_pg_details["quantity"]
            discount_percentage = each_pg_details["discount_percentage"]

            difference_date = (end_time_date_object - start_time_date_object)
            total_hours = ceil((difference_date.total_seconds() // 60) / 60)
            days = total_hours // 24
            hours = total_hours % 24

            total_price = discounted_price = 0
            if each_product.price_type == PriceTypes.HOUR.value:
                total_price = float(each_product.price) * total_hours * quantity
                discounted_price = float(each_product.discounted_price) * total_hours * quantity
            elif each_product.price_type == PriceTypes.DAY.value:
                total_price = (float(each_product.price) * (days + hours / 24)) * quantity
                discounted_price = (float(each_product.discounted_price) * (days + hours / 24)) * quantity

            starting_prices[each_product.id] = {
                "total_price": total_price,
                "discounted_price": discounted_price
            }

        return starting_prices

    def calculate_final_prices(self, products):
        final_prices = defaultdict()
        for each_product in products:
            product_details = products[each_product]
            quantity = product_details["quantity"]
            start_time = datetime.strptime(product_details["start_time"], get_date_format())
            booking_end_time = datetime.strptime(product_details["booking_end_time"], get_date_format())
            present_end_time = datetime.strptime(product_details["present_end_time"], get_date_format())
            booking_difference_date = (booking_end_time - start_time)
            booking_total_hours = ceil((booking_difference_date.total_seconds() // 60) / 60)
            days = booking_total_hours // 24
            hours = booking_total_hours % 24
            excess_total_hours = excess_days = excess_hours = 0
            if present_end_time > booking_end_time:
                excess_difference_date = (present_end_time - booking_end_time)
                excess_total_hours = ceil((excess_difference_date.total_seconds() // 60) / 60)
                excess_days = excess_total_hours // 24
                excess_hours = excess_total_hours % 24

            duration_price = excess_duration_price = 0
            if product_details["price_type"] == PriceTypes.HOUR.value:
                duration_price = float(product_details["price"]) * booking_total_hours * quantity
                excess_duration_price = float(product_details["price"]) * excess_total_hours * quantity
            elif product_details["price_type"] == PriceTypes.DAY.value:
                duration_price = (float(product_details["price"]) * (days + hours / 24)) * quantity
                excess_duration_price = (float(product_details["price"]) * (excess_days + excess_hours / 24)) * quantity

            total_price = duration_price + excess_duration_price

            final_prices[each_product] = {
                "final_price": total_price,
                "discounted_price": total_price
            }
        return final_prices

    def check_valid_duration(self, product_ids, start_time, end_time):
        is_valid = True
        errors = defaultdict(list)
        return is_valid, errors