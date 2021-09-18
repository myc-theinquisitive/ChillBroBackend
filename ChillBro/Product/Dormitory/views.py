from datetime import datetime
from math import ceil
from typing import List, Dict
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from Bookings.helpers import get_date_format
from ChillBro.constants import PriceTypes
from .models import DormitoryAmenities, DormitoryRoom, DormitoryAvailableAmenities
from .serializers import DormitoryAmenityIsAvailableSerializer, DormitoryAvailableAmenitiesSerializer, DormitoryRoomSerializer, \
    DormitoryAvailableAmenitiesUpdateSerializer, DormitoryAmenitiesSerializer
from ..BaseProduct.models import Product
from ..product_interface import ProductInterface
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsGet


def validate_dormitory_amenity_ids(dormitory_amenity_ids: List[int]) -> (bool, List[int]):
    existing_dormitory_amenities = DormitoryAmenities.objects.filter(id__in=dormitory_amenity_ids).values_list('id', flat=True)
    if len(existing_dormitory_amenities) != len(dormitory_amenity_ids):
        return False, set(dormitory_amenity_ids) - set(existing_dormitory_amenities)
    return True, []


def validate_dormitory_ids(dormitory_ids: List[int]) -> (bool, List[int]):
    existing_dormitory_ids = DormitoryRoom.objects.filter(id__in=dormitory_ids)\
        .values_list('id', flat=True)
    if len(existing_dormitory_ids) != len(dormitory_ids):
        return False, set(dormitory_ids) - set(existing_dormitory_ids)
    return True, []


def validate_dormitory_available_dormitory_amenities_ids(dormitory_room_id: int, dormitory_available_amenity_ids: List[int])\
        -> (bool, List[int]):
    existing_dormitory_available_amenity_ids \
        = DormitoryAvailableAmenities.objects.filter(id__in=dormitory_available_amenity_ids, dormitory_room_id=dormitory_room_id)\
        .values_list('id', flat=True)
    if len(existing_dormitory_available_amenity_ids) != len(dormitory_available_amenity_ids):
        return False, set(dormitory_available_amenity_ids) - set(existing_dormitory_available_amenity_ids)
    return True, []


class DormitoryAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet)
    queryset = DormitoryAmenities.objects.all()
    serializer_class = DormitoryAmenitiesSerializer


class DormitoryAvailableAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = DormitoryAvailableAmenities.objects.all()
    serializer_class = DormitoryAvailableAmenitiesSerializer


class DormitoryAvailableAmenitiesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = DormitoryAvailableAmenities.objects.all()
    serializer_class = DormitoryAvailableAmenitiesSerializer


class DormitoryView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.dormitory_room_serializer = None
        self.dormitory_amenities_data = None

        self.dormitory_room_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, dormitory_room_data):
        if dormitory_room_data:
            self.dormitory_amenities_data = dormitory_room_data.pop("dormitory_amenities", None)

        dormitory_room_object_defined = self.dormitory_room_object is not None
        dormitory_room_data_defined = dormitory_room_data is not None

        # for update
        if dormitory_room_object_defined and dormitory_room_data_defined:
            self.dormitory_room_serializer = DormitoryRoomSerializer(self.dormitory_room_object, data=dormitory_room_data)
        # for create
        elif dormitory_room_data_defined:
            self.dormitory_room_serializer = DormitoryRoomSerializer(data=dormitory_room_data)
        # for get
        elif dormitory_room_object_defined:
            self.dormitory_room_serializer = DormitoryRoomSerializer(self.dormitory_room_object)
        else:
            self.dormitory_room_serializer = DormitoryRoomSerializer()

    def validate_create_data(self, dormitory_room_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(dormitory_room_data)

        dormitory_data_valid = self.dormitory_room_serializer.is_valid()
        if not dormitory_data_valid:
            is_valid = False
            errors.update(self.dormitory_room_serializer.errors)

        # Additional validations except serializer validations
        dormitory_amenity_ids = []
        for dormitory_amenity_dict in self.dormitory_amenities_data:
            if "dormitory_amenity" not in dormitory_amenity_dict:
                is_valid = False
                errors["dormitory_amenity"].append("This field is required.")
                continue
            if "is_available" not in dormitory_amenity_dict:
                is_valid = False
                errors["is_available"].append("This field is required.")
                continue
            dormitory_amenity_ids.append(dormitory_amenity_dict["dormitory_amenity"])

        dormitory_amenity_ids_valid, invalid_ids = validate_dormitory_amenity_ids(dormitory_amenity_ids)
        if not dormitory_amenity_ids_valid:
            is_valid = False
            errors["invalid_dormitory_amenity_ids"] = invalid_ids

        return is_valid, errors

    def create(self, dormitory_room_data):
        """
        dormitory_room: {
            "product_id": string, # internal data need not be validated
            "dormitory_amenities": [
                {
                    "dormitory_amenity": string,
                    "is_available": boolean
                }
            ]
        }
        """

        dormitory_room_object = self.dormitory_room_serializer.create(dormitory_room_data)

        for dormitory_amenity in self.dormitory_amenities_data:
            dormitory_amenity["dormitory_room"] = dormitory_room_object.id

        dormitory_available_dormitory_amenities_serializer = DormitoryAvailableAmenitiesSerializer()
        dormitory_available_dormitory_amenities_serializer.bulk_create(self.dormitory_amenities_data)

        return {
            "id": dormitory_room_object.id
        }

    def validate_update_data(self, dormitory_room_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.dormitory_room_object \
                = DormitoryRoom.objects.get(product_id=dormitory_room_data["product"])
        except DormitoryRoom.DoesNotExist:
            return False, {"errors": "DormitoryRoom does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(dormitory_room_data)

        dormitory_data_valid = self.dormitory_room_serializer.is_valid()
        if not dormitory_data_valid:
            is_valid = False
            errors.update(self.dormitory_room_serializer.errors)

        dormitory_available_dormitory_amenities_update_serializer = DormitoryAvailableAmenitiesUpdateSerializer(data=self.dormitory_amenities_data)
        dormitory_available_dormitory_amenities_update_data_valid = dormitory_available_dormitory_amenities_update_serializer.is_valid()

        if not dormitory_available_dormitory_amenities_update_data_valid:
            is_valid = False
            errors.update(dormitory_available_dormitory_amenities_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        dormitory_amenity_ids = []
        dormitory_available_amenity_ids = []
        for dormitory_amenity in self.dormitory_amenities_data["add"]:
            dormitory_available_dormitory_amenities_exists = DormitoryAvailableAmenities.objects\
                .filter(dormitory_room=self.dormitory_room_object, dormitory_amenity_id=dormitory_amenity["dormitory_amenity"]).exists()
            if dormitory_available_dormitory_amenities_exists:
                is_valid = False
                errors["DormitoryRoom-Amenity"].append("DormitoryRoom-{0}, Amenity-{1}: Already Exists!"
                                                   .format(self.dormitory_room_object.id, dormitory_amenity["dormitory_amenity"]))

            dormitory_amenity["dormitory_room"] = self.dormitory_room_object.id
            dormitory_amenity_ids.append(dormitory_amenity["dormitory_amenity"])

        for dormitory_amenity in self.dormitory_amenities_data["change"]:
            dormitory_available_amenity_ids.append(dormitory_amenity["id"])

        for dormitory_amenity in self.dormitory_amenities_data["delete"]:
            dormitory_available_amenity_ids.append(dormitory_amenity["id"])

        dormitory_amenity_ids_valid, invalid_dormitory_amenity_ids = validate_dormitory_amenity_ids(dormitory_amenity_ids)
        if not dormitory_amenity_ids_valid:
            is_valid = False
            errors["invalid_dormitory_amenity_ids"] = invalid_dormitory_amenity_ids

        dormitory_available_dormitory_amenities_ids_valid, invalid_dormitory_available_dormitory_amenities_ids \
            = validate_dormitory_available_dormitory_amenities_ids(self.dormitory_room_object.id, dormitory_available_amenity_ids)
        if not dormitory_available_dormitory_amenities_ids_valid:
            is_valid = False
            errors["invalid_dormitory_available_dormitory_amenities_ids"] = invalid_dormitory_available_dormitory_amenities_ids

        return is_valid, errors

    def update(self, dormitory_room_data):
        """
        dormitory_room: {
            "product_id": string, # internal data need not be validated,
            "dormitory_amenities": {
                "add": [
                    {
                        "dormitory_amenity": string,
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

        self.dormitory_room_serializer.update(self.dormitory_room_object, dormitory_room_data)

        dormitory_available_dormitory_amenities_serializer = DormitoryAvailableAmenitiesSerializer()
        dormitory_available_dormitory_amenities_serializer.bulk_create(self.dormitory_amenities_data["add"])
        dormitory_available_dormitory_amenities_serializer.bulk_update(self.dormitory_amenities_data["change"])
        dormitory_available_dormitory_amenities_serializer.bulk_delete(self.dormitory_amenities_data["delete"])

    @staticmethod
    def convert_available_dormitory_amenities_to_dict(available_dormitory_amenity):
        image_url = available_dormitory_amenity.dormitory_amenity.icon_url.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        return {
            "id": available_dormitory_amenity.id,
            "name": available_dormitory_amenity.dormitory_amenity.name,
            "icon_url": image_url,
            "is_available": available_dormitory_amenity.is_available
        }

    @staticmethod
    def update_dormitory_room_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.dormitory_room_object = DormitoryRoom.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        dormitory_room_data = self.dormitory_room_serializer.data
        dormitory_room_data = self.update_dormitory_room_response(dormitory_room_data)

        available_dormitory_amenities = DormitoryAvailableAmenities.objects.select_related('dormitory_amenity')\
            .filter(dormitory_room=self.dormitory_room_object)

        available_dormitory_amenities_data = []
        for available_dormitory_amenity in available_dormitory_amenities:
            available_dormitory_amenity_data = self.convert_available_dormitory_amenities_to_dict(available_dormitory_amenity)
            available_dormitory_amenities_data.append(available_dormitory_amenity_data)

        dormitory_room_data["available_dormitory_amenities"] = available_dormitory_amenities_data
        return dormitory_room_data

    def get_by_ids(self, product_ids):
        dormitory_rooms = DormitoryRoom.objects.filter(product_id__in=product_ids)

        dormitory_rooms_serializer = DormitoryRoomSerializer(dormitory_rooms, many=True)
        dormitory_rooms_data = dormitory_rooms_serializer.data

        dormitory_room_ids = []
        for dormitory_room_data in dormitory_rooms_data:
            dormitory_room_data = self.update_dormitory_room_response(dormitory_room_data)
            dormitory_room_ids.append(dormitory_room_data["id"])

        available_dormitory_amenities = DormitoryAvailableAmenities.objects.select_related('dormitory_amenity') \
            .filter(dormitory_room__in=dormitory_room_ids)
        dormitory_room_wise_available_dormitory_amenities_dict = defaultdict(list)
        for available_dormitory_amenity in available_dormitory_amenities:
            available_dormitory_amenity_data = self.convert_available_dormitory_amenities_to_dict(available_dormitory_amenity)
            dormitory_room_wise_available_dormitory_amenities_dict[available_dormitory_amenity.dormitory_room_id].append(
                available_dormitory_amenity_data)

        for dormitory_room_data in dormitory_rooms_data:
            dormitory_room_data["available_dormitory_amenities"] = dormitory_room_wise_available_dormitory_amenities_dict[dormitory_room_data["id"]]

        return dormitory_rooms_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        products = Product.objects.filter(id__in=product_ids)
        starting_prices = defaultdict()
        for each_product in products:
            each_hire_a_vehicle_details = product_details_with_ids[each_product.product_id]
            start_time_date_object = each_hire_a_vehicle_details['start_time']
            end_time_date_object = each_hire_a_vehicle_details['end_time']
            quantity = each_hire_a_vehicle_details["quantity"]
            discount_percentage = each_hire_a_vehicle_details["discount_percentage"]

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