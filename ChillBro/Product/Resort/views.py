from datetime import datetime
from math import ceil
from typing import List, Dict
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from Bookings.helpers import get_date_format
from ChillBro.constants import PriceTypes
from .models import ResortAmenities, ResortRoom, ResortAvailableAmenities
from .serializers import ResortAmenityIsAvailableSerializer, ResortAvailableAmenitiesSerializer, ResortRoomSerializer, \
    ResortAvailableAmenitiesUpdateSerializer, ResortAmenitiesSerializer
from ..BaseProduct.models import Product
from ..product_interface import ProductInterface
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsGet


def validate_resort_amenity_ids(resort_amenity_ids: List[int]) -> (bool, List[int]):
    existing_resort_amenities = ResortAmenities.objects.filter(id__in=resort_amenity_ids).values_list('id', flat=True)
    if len(existing_resort_amenities) != len(resort_amenity_ids):
        return False, set(resort_amenity_ids) - set(existing_resort_amenities)
    return True, []


def validate_resort_ids(resort_ids: List[int]) -> (bool, List[int]):
    existing_resort_ids = ResortRoom.objects.filter(id__in=resort_ids)\
        .values_list('id', flat=True)
    if len(existing_resort_ids) != len(resort_ids):
        return False, set(resort_ids) - set(existing_resort_ids)
    return True, []


def validate_resort_available_resort_amenities_ids(resort_room_id: int, resort_available_amenity_ids: List[int])\
        -> (bool, List[int]):
    existing_resort_available_amenity_ids \
        = ResortAvailableAmenities.objects.filter(id__in=resort_available_amenity_ids, resort_room_id=resort_room_id)\
        .values_list('id', flat=True)
    if len(existing_resort_available_amenity_ids) != len(resort_available_amenity_ids):
        return False, set(resort_available_amenity_ids) - set(existing_resort_available_amenity_ids)
    return True, []


class ResortAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet)
    queryset = ResortAmenities.objects.all()
    serializer_class = ResortAmenitiesSerializer


class ResortAvailableAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ResortAvailableAmenities.objects.all()
    serializer_class = ResortAvailableAmenitiesSerializer


class ResortAvailableAmenitiesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = ResortAvailableAmenities.objects.all()
    serializer_class = ResortAvailableAmenitiesSerializer


class ResortView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.resort_room_serializer = None
        self.resort_amenities_data = None

        self.resort_room_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, resort_room_data):
        if resort_room_data:
            self.resort_amenities_data = resort_room_data.pop("resort_amenities", None)

        resort_room_object_defined = self.resort_room_object is not None
        resort_room_data_defined = resort_room_data is not None

        # for update
        if resort_room_object_defined and resort_room_data_defined:
            self.resort_room_serializer = ResortRoomSerializer(self.resort_room_object, data=resort_room_data)
        # for create
        elif resort_room_data_defined:
            self.resort_room_serializer = ResortRoomSerializer(data=resort_room_data)
        # for get
        elif resort_room_object_defined:
            self.resort_room_serializer = ResortRoomSerializer(self.resort_room_object)
        else:
            self.resort_room_serializer = ResortRoomSerializer()

    def validate_create_data(self, resort_room_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(resort_room_data)

        resort_data_valid = self.resort_room_serializer.is_valid()
        if not resort_data_valid:
            is_valid = False
            errors.update(self.resort_room_serializer.errors)

        # Additional validations except serializer validations
        resort_amenity_ids = []
        for resort_amenity_dict in self.resort_amenities_data:
            if "resort_amenity" not in resort_amenity_dict:
                is_valid = False
                errors["resort_amenity"].append("This field is required.")
                continue
            if "is_available" not in resort_amenity_dict:
                is_valid = False
                errors["is_available"].append("This field is required.")
                continue
            resort_amenity_ids.append(resort_amenity_dict["resort_amenity"])

        resort_amenity_ids_valid, invalid_ids = validate_resort_amenity_ids(resort_amenity_ids)
        if not resort_amenity_ids_valid:
            is_valid = False
            errors["invalid_resort_amenity_ids"] = invalid_ids

        return is_valid, errors

    def create(self, resort_room_data):
        """
        resort_room: {
            "product_id": string, # internal data need not be validated
            "resort_amenities": [
                {
                    "resort_amenity": string,
                    "is_available": boolean
                }
            ]
        }
        """

        resort_room_object = self.resort_room_serializer.create(resort_room_data)

        for resort_amenity in self.resort_amenities_data:
            resort_amenity["resort_room"] = resort_room_object.id

        resort_available_resort_amenities_serializer = ResortAvailableAmenitiesSerializer()
        resort_available_resort_amenities_serializer.bulk_create(self.resort_amenities_data)

        return {
            "id": resort_room_object.id
        }

    def validate_update_data(self, resort_room_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.resort_room_object \
                = ResortRoom.objects.get(product_id=resort_room_data["product"])
        except ResortRoom.DoesNotExist:
            return False, {"errors": "ResortRoom does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(resort_room_data)

        resort_data_valid = self.resort_room_serializer.is_valid()
        if not resort_data_valid:
            is_valid = False
            errors.update(self.resort_room_serializer.errors)

        resort_available_resort_amenities_update_serializer = ResortAvailableAmenitiesUpdateSerializer(data=self.resort_amenities_data)
        resort_available_resort_amenities_update_data_valid = resort_available_resort_amenities_update_serializer.is_valid()

        if not resort_available_resort_amenities_update_data_valid:
            is_valid = False
            errors.update(resort_available_resort_amenities_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        resort_amenity_ids = []
        resort_available_amenity_ids = []
        for resort_amenity in self.resort_amenities_data["add"]:
            resort_available_resort_amenities_exists = ResortAvailableAmenities.objects\
                .filter(resort_room=self.resort_room_object, resort_amenity_id=resort_amenity["resort_amenity"]).exists()
            if resort_available_resort_amenities_exists:
                is_valid = False
                errors["ResortRoom-Amenity"].append("ResortRoom-{0}, Amenity-{1}: Already Exists!"
                                                   .format(self.resort_room_object.id, resort_amenity["resort_amenity"]))

            resort_amenity["resort_room"] = self.resort_room_object.id
            resort_amenity_ids.append(resort_amenity["resort_amenity"])

        for resort_amenity in self.resort_amenities_data["change"]:
            resort_available_amenity_ids.append(resort_amenity["id"])

        for resort_amenity in self.resort_amenities_data["delete"]:
            resort_available_amenity_ids.append(resort_amenity["id"])

        resort_amenity_ids_valid, invalid_resort_amenity_ids = validate_resort_amenity_ids(resort_amenity_ids)
        if not resort_amenity_ids_valid:
            is_valid = False
            errors["invalid_resort_amenity_ids"] = invalid_resort_amenity_ids

        resort_available_resort_amenities_ids_valid, invalid_resort_available_resort_amenities_ids \
            = validate_resort_available_resort_amenities_ids(self.resort_room_object.id, resort_available_amenity_ids)
        if not resort_available_resort_amenities_ids_valid:
            is_valid = False
            errors["invalid_resort_available_resort_amenities_ids"] = invalid_resort_available_resort_amenities_ids

        return is_valid, errors

    def update(self, resort_room_data):
        """
        resort_room: {
            "product_id": string, # internal data need not be validated,
            "resort_amenities": {
                "add": [
                    {
                        "resort_amenity": string,
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

        self.resort_room_serializer.update(self.resort_room_object, resort_room_data)

        resort_available_resort_amenities_serializer = ResortAvailableAmenitiesSerializer()
        resort_available_resort_amenities_serializer.bulk_create(self.resort_amenities_data["add"])
        resort_available_resort_amenities_serializer.bulk_update(self.resort_amenities_data["change"])
        resort_available_resort_amenities_serializer.bulk_delete(self.resort_amenities_data["delete"])

    @staticmethod
    def convert_available_resort_amenities_to_dict(available_resort_amenity):
        image_url = available_resort_amenity.resort_amenity.icon_url.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        return {
            "id": available_resort_amenity.id,
            "name": available_resort_amenity.resort_amenity.name,
            "icon_url": image_url,
            "is_available": available_resort_amenity.is_available
        }

    @staticmethod
    def update_resort_room_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.resort_room_object = ResortRoom.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        resort_room_data = self.resort_room_serializer.data
        resort_room_data = self.update_resort_room_response(resort_room_data)

        available_resort_amenities = ResortAvailableAmenities.objects.select_related('resort_amenity')\
            .filter(resort_room=self.resort_room_object)

        available_resort_amenities_data = []
        for available_resort_amenity in available_resort_amenities:
            available_resort_amenity_data = self.convert_available_resort_amenities_to_dict(available_resort_amenity)
            available_resort_amenities_data.append(available_resort_amenity_data)

        resort_room_data["available_resort_amenities"] = available_resort_amenities_data
        return resort_room_data

    def get_by_ids(self, product_ids):
        resort_rooms = ResortRoom.objects.filter(product_id__in=product_ids)

        resort_rooms_serializer = ResortRoomSerializer(resort_rooms, many=True)
        resort_rooms_data = resort_rooms_serializer.data

        resort_room_ids = []
        for resort_room_data in resort_rooms_data:
            resort_room_data = self.update_resort_room_response(resort_room_data)
            resort_room_ids.append(resort_room_data["id"])

        available_resort_amenities = ResortAvailableAmenities.objects.select_related('resort_amenity') \
            .filter(resort_room__in=resort_room_ids)
        resort_room_wise_available_resort_amenities_dict = defaultdict(list)
        for available_resort_amenity in available_resort_amenities:
            available_resort_amenity_data = self.convert_available_resort_amenities_to_dict(available_resort_amenity)
            resort_room_wise_available_resort_amenities_dict[available_resort_amenity.resort_room_id].append(
                available_resort_amenity_data)

        for resort_room_data in resort_rooms_data:
            resort_room_data["available_resort_amenities"] = resort_room_wise_available_resort_amenities_dict[resort_room_data["id"]]

        return resort_rooms_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        products = Product.objects.filter(id__in=product_ids)
        starting_prices = defaultdict()
        for each_product in products:
            each_resort_details = product_details_with_ids[each_product.product_id]
            start_time_date_object = each_resort_details['start_time']
            end_time_date_object = each_resort_details['end_time']
            quantity = each_resort_details["quantity"]
            discount_percentage = each_resort_details["discount_percentage"]

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