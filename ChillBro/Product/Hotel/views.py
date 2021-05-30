from typing import List, Dict
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Amenities, HotelRoom, HotelAvailableAmenities
from .serializers import AmenitiesSerializer, HotelAvailableAmenitiesSerializer, HotelRoomSerializer, \
    HotelAvailableAmenitiesUpdateSerializer
from ..product_interface import ProductInterface
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsGet


def validate_amenity_ids(amenity_ids: List[int]) -> (bool, List[int]):
    existing_amenities = Amenities.objects.filter(id__in=amenity_ids).values_list('id', flat=True)
    if len(existing_amenities) != len(amenity_ids):
        return False, set(amenity_ids) - set(existing_amenities)
    return True, []


def validate_hotel_ids(hotel_ids: List[int]) -> (bool, List[int]):
    existing_hotel_ids = HotelRoom.objects.filter(id__in=hotel_ids)\
        .values_list('id', flat=True)
    if len(existing_hotel_ids) != len(hotel_ids):
        return False, set(hotel_ids) - set(existing_hotel_ids)
    return True, []


def validate_hotel_available_amenities_ids(hotel_room_id: int, hotel_available_amenity_ids: List[int])\
        -> (bool, List[int]):
    existing_hotel_available_amenity_ids \
        = HotelAvailableAmenities.objects.filter(id__in=hotel_available_amenity_ids, hotel_room_id=hotel_room_id)\
        .values_list('id', flat=True)
    if len(existing_hotel_available_amenity_ids) != len(hotel_available_amenity_ids):
        return False, set(hotel_available_amenity_ids) - set(existing_hotel_available_amenity_ids)
    return True, []


class AmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet)
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer


class HotelAvailableAmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = HotelAvailableAmenities.objects.all()
    serializer_class = HotelAvailableAmenitiesSerializer


class HotelAvailableAmenitiesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = HotelAvailableAmenities.objects.all()
    serializer_class = HotelAvailableAmenitiesSerializer


class HotelView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.hotel_room_serializer = None
        self.amenities_data = None

        self.hotel_room_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, hotel_room_data):
        if hotel_room_data:
            self.amenities_data = hotel_room_data.pop("amenities", None)

        hotel_room_object_defined = self.hotel_room_object is not None
        hotel_room_data_defined = hotel_room_data is not None

        # for update
        if hotel_room_object_defined and hotel_room_data_defined:
            self.hotel_room_serializer = HotelRoomSerializer(self.hotel_room_object, data=hotel_room_data)
        # for create
        elif hotel_room_data_defined:
            self.hotel_room_serializer = HotelRoomSerializer(data=hotel_room_data)
        # for get
        elif hotel_room_object_defined:
            self.hotel_room_serializer = HotelRoomSerializer(self.hotel_room_object)
        else:
            self.hotel_room_serializer = HotelRoomSerializer()

    def validate_create_data(self, hotel_room_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(hotel_room_data)

        hotel_data_valid = self.hotel_room_serializer.is_valid()
        if not hotel_data_valid:
            is_valid = False
            errors.update(self.hotel_room_serializer.errors)

        # Additional validations except serializer validations
        amenity_ids = []
        for amenity_dict in self.amenities_data:
            if "amenity" not in amenity_dict:
                is_valid = False
                errors["amenity"].append("This field is required.")
                continue
            if "is_available" not in amenity_dict:
                is_valid = False
                errors["is_available"].append("This field is required.")
                continue
            amenity_ids.append(amenity_dict["amenity"])

        amenity_ids_valid, invalid_ids = validate_amenity_ids(amenity_ids)
        if not amenity_ids_valid:
            is_valid = False
            errors["invalid_amenity_ids"] = invalid_ids

        return is_valid, errors

    def create(self, hotel_room_data):
        """
        hotel_room: {
            "product_id": string, # internal data need not be validated
            "max_no_of_people": int,
            "amenities": [
                {
                    "amenity": string,
                    "is_available": boolean
                }
            ]
        }
        """

        hotel_room_object = self.hotel_room_serializer.create(hotel_room_data)

        for amenity in self.amenities_data:
            amenity["hotel_room"] = hotel_room_object.id

        hotel_available_amenities_serializer = HotelAvailableAmenitiesSerializer()
        hotel_available_amenities_serializer.bulk_create(self.amenities_data)

        return {
            "id": hotel_room_object.id
        }

    def validate_update_data(self, hotel_room_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.hotel_room_object \
                = HotelRoom.objects.get(product_id=hotel_room_data["product"])
        except HotelRoom.DoesNotExist:
            return False, {"errors": "HotelRoom does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(hotel_room_data)

        hotel_data_valid = self.hotel_room_serializer.is_valid()
        if not hotel_data_valid:
            is_valid = False
            errors.update(self.hotel_room_serializer.errors)

        hotel_available_amenities_update_serializer = HotelAvailableAmenitiesUpdateSerializer(data=self.amenities_data)
        hotel_available_amenities_update_data_valid = hotel_available_amenities_update_serializer.is_valid()

        if not hotel_available_amenities_update_data_valid:
            is_valid = False
            errors.update(hotel_available_amenities_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        amenity_ids = []
        hotel_available_amenity_ids = []
        for amenity in self.amenities_data["add"]:
            hotel_available_amenities_exists = HotelAvailableAmenities.objects\
                .filter(hotel_room=self.hotel_room_object, amenity_id=amenity["amenity"]).exists()
            if hotel_available_amenities_exists:
                is_valid = False
                errors["HotelRoom-Amenity"].append("HotelRoom-{0}, Amenity-{1}: Already Exists!"
                                                   .format(self.hotel_room_object.id, amenity["amenity"]))

            amenity["hotel_room"] = self.hotel_room_object.id
            amenity_ids.append(amenity["amenity"])

        for amenity in self.amenities_data["change"]:
            hotel_available_amenity_ids.append(amenity["id"])

        for amenity in self.amenities_data["delete"]:
            hotel_available_amenity_ids.append(amenity["id"])

        amenity_ids_valid, invalid_amenity_ids = validate_amenity_ids(amenity_ids)
        if not amenity_ids_valid:
            is_valid = False
            errors["invalid_amenity_ids"] = invalid_amenity_ids

        hotel_available_amenities_ids_valid, invalid_hotel_available_amenities_ids \
            = validate_hotel_available_amenities_ids(self.hotel_room_object.id, hotel_available_amenity_ids)
        if not hotel_available_amenities_ids_valid:
            is_valid = False
            errors["invalid_hotel_available_amenities_ids"] = invalid_hotel_available_amenities_ids

        return is_valid, errors

    def update(self, hotel_room_data):
        """
        hotel_room: {
            "product_id": string, # internal data need not be validated,
            "max_no_of_people": int,
            "amenities": {
                "add": [
                    {
                        "amenity": string,
                        "is_available": boolean
                    }
                ]
                "change": [
                    {
                        "id": string,
                        "is_available": boolean
                    }
                ]
                "delete": [
                    {
                        "id": string
                    }
                ]
            }
        }
        """

        self.hotel_room_serializer.update(self.hotel_room_object, hotel_room_data)

        hotel_available_amenities_serializer = HotelAvailableAmenitiesSerializer()
        hotel_available_amenities_serializer.bulk_create(self.amenities_data["add"])
        hotel_available_amenities_serializer.bulk_update(self.amenities_data["change"])
        hotel_available_amenities_serializer.bulk_delete(self.amenities_data["delete"])

    @staticmethod
    def convert_available_amenities_to_dict(available_amenity):
        image_url = available_amenity.amenity.icon_url.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        return {
            "id": available_amenity.id,
            "name": available_amenity.amenity.name,
            "icon_url": image_url,
            "is_available": available_amenity.is_available
        }

    @staticmethod
    def update_hotel_room_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.hotel_room_object = HotelRoom.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        hotel_room_data = self.hotel_room_serializer.data
        hotel_room_data = self.update_hotel_room_response(hotel_room_data)

        available_amenities = HotelAvailableAmenities.objects.select_related('amenity')\
            .filter(hotel_room=self.hotel_room_object)

        available_amenities_data = []
        for available_amenity in available_amenities:
            available_amenity_data = self.convert_available_amenities_to_dict(available_amenity)
            available_amenities_data.append(available_amenity_data)

        hotel_room_data["available_amenities"] = available_amenities_data
        return hotel_room_data

    def get_by_ids(self, product_ids):
        hotel_rooms = HotelRoom.objects.filter(product_id__in=product_ids)

        hotel_rooms_serializer = HotelRoomSerializer(hotel_rooms, many=True)
        hotel_rooms_data = hotel_rooms_serializer.data

        hotel_room_ids = []
        for hotel_room_data in hotel_rooms_data:
            hotel_room_data = self.update_hotel_room_response(hotel_room_data)
            hotel_room_ids.append(hotel_room_data["id"])

        available_amenities = HotelAvailableAmenities.objects.select_related('amenity') \
            .filter(hotel_room__in=hotel_room_ids)
        hotel_room_wise_available_amenities_dict = defaultdict(list)
        for available_amenity in available_amenities:
            available_amenity_data = self.convert_available_amenities_to_dict(available_amenity)
            hotel_room_wise_available_amenities_dict[available_amenity.hotel_room_id].append(
                available_amenity_data)

        for hotel_room_data in hotel_rooms_data:
            hotel_room_data["available_amenities"] = hotel_room_wise_available_amenities_dict[hotel_room_data["id"]]

        return hotel_rooms_data
