from Product.product_interface import ProductInterface
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from rest_framework import generics
from .serializers import TravelPackageSerializer, PackagePlacesSerializer, TravelPackageImageSerializer
from .models import TravelPackage, PackagePlaces, TravelPackageImage
from typing import Dict
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .wrapper import get_travel_package_id_wise_vehicles_count, get_place_id_wise_details, validate_place_ids
from datetime import timedelta, datetime


class TravelPackageView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.travel_package_serializer = None
        self.travel_package_object = None

        self.travel_package_images = []
        self.places_data = {}

    # initialize the instance variables before accessing
    def initialize_product_class(self, travel_package_data):
        travel_package_object_defined = self.travel_package_object is not None
        travel_package_data_defined = travel_package_data is not None

        if travel_package_data_defined:
            if "images" in travel_package_data:
                self.travel_package_images = travel_package_data.pop("images", [])
            if "places" in travel_package_data:
                self.places_data = travel_package_data.pop("places", [])

        # for update
        if travel_package_object_defined and travel_package_data_defined:
            self.travel_package_serializer = TravelPackageSerializer(
                self.travel_package_object, data=travel_package_data)
        # for create
        elif travel_package_data_defined:
            self.travel_package_serializer = TravelPackageSerializer(data=travel_package_data)
        # for get
        elif travel_package_object_defined:
            self.travel_package_serializer = TravelPackageSerializer(self.travel_package_object)
        else:
            self.travel_package_serializer = TravelPackageSerializer()

    def validate_create_data(self, travel_package_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(travel_package_data)

        travel_package_data_valid = self.travel_package_serializer.is_valid()
        if not travel_package_data_valid:
            is_valid = False
            errors.update(self.travel_package_serializer.errors)

        # Validating places
        package_places_serializer = PackagePlacesSerializer(data=self.places_data, many=True)
        if not package_places_serializer.is_valid():
            is_valid = False
            errors["places"] = package_places_serializer.errors
        # TODO: validate place ids

        place_ids = list(map(lambda x: x['place'], self.places_data))
        is_place_ids_valid, invalid_place_ids = validate_place_ids(place_ids)

        if not is_place_ids_valid:
            is_valid = False
            errors['incorrect place ids'] = invalid_place_ids

        # Validating images
        travel_package_image_serializer = TravelPackageImageSerializer(data=self.travel_package_images, many=True)
        if not travel_package_image_serializer.is_valid():
            is_valid = False
            errors["images"] = travel_package_image_serializer.errors

        return is_valid, errors

    def create(self, travel_package_data):
        """
        {
            "product_id": string, # internal data need not be validated,
            "travel_package": {
                duration_in_days: int,
                duration_in_nights: int,
                starting_point: string,
                places: [
                    {
                        'place': string,
                        'order': int,
                        'in_return': bool,
                        "spending_time": int,
                        "duration_to_reach": int
                    }
                ]
                images: [
                    {
                        'image': file,
                        'order': int
                    }
                ]
            }
        }
        """

        travel_package_object = self.travel_package_serializer.create(travel_package_data)

        # Add Places to Travel Package
        for place_dict in self.places_data:
            place_dict["travel_package"] = travel_package_object.id
        PackagePlacesSerializer.bulk_create(self.places_data)

        # Add Images to Travel Package
        for image_dict in self.travel_package_images:
            image_dict["travel_package"] = travel_package_object.id
        TravelPackageImageSerializer.bulk_create(self.travel_package_images)

        return {
            "id": travel_package_object.id
        }

    def validate_update_data(self, travel_package_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.travel_package_object \
                = TravelPackage.objects.get(id=travel_package_data["id"])
        except TravelPackage.DoesNotExist:
            return False, {"errors": "Travel Package does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(travel_package_data)

        travel_package_data_valid = self.travel_package_serializer.is_valid()
        if not travel_package_data_valid:
            is_valid = False
            errors.update(self.travel_package_serializer.errors)

        # validate places for travel package
        if self.places_data:
            if "add" in self.places_data:
                place_ids = []
                for travel_package_place in self.places_data["add"]:
                    place_ids.append(travel_package_place["place"])

                # TODO: validate place ids

                is_place_ids_valid, invalid_place_ids = validate_place_ids(place_ids)

                if not is_place_ids_valid:
                    is_valid = False
                    errors['incorrect place ids'] = invalid_place_ids

            # No validations required for delete

        return is_valid, errors

    def update(self, travel_package_data):
        """
        {
            duration_in_days: int,
            duration_in_nights: int,
            starting_point: string,
            'places': {
                'add': [
                    {
                        'place': string,
                        'order': int,
                        'in_return': bool,
                        "spending_time": int,
                        "duration_to_reach": int
                    },
                ],
                'delete': ['place_id']
            }
        }
        """

        self.travel_package_serializer.update(self.travel_package_object, travel_package_data)

        # Add Places to Travel Package
        travel_package_places_add_dicts = []
        if "add" in self.places_data:
            for place_dict in self.places_data["add"]:
                travel_package_place_dict = {
                    "travel_package": self.travel_package_object.id,
                    "place": place_dict["place"],
                    "in_return": place_dict["in_return"],
                    "order": place_dict["order"],
                    "spending_time": place_dict["spending_time"],
                    "duration_to_reach": place_dict["duration_to_reach"]
                }
                travel_package_places_add_dicts.append(travel_package_place_dict)
            PackagePlacesSerializer.bulk_create(travel_package_places_add_dicts)

        # Deleting Places for Travel Package
        if "delete" in self.places_data:
            delete_places = self.places_data["delete"]
            PackagePlacesSerializer.bulk_delete(self.travel_package_object.id, delete_places)

    @staticmethod
    def get_travel_package_id_wise_places_details(travel_package_ids, start_time):

        travel_package_places = PackagePlaces.objects.filter(travel_package_id__in=travel_package_ids)

        place_ids = []
        for travel_package_place in travel_package_places:
            place_ids.append(travel_package_place.place_id)

        place_id_wise_details = get_place_id_wise_details(place_ids)

        travel_package_id_wise_forward_places = defaultdict(list)
        travel_package_id_wise_return_places = defaultdict(list)
        for travel_package_place in travel_package_places:
            arrival_time = start_time + timedelta(minutes=travel_package_place.duration_to_reach)
            departure_time = arrival_time + timedelta(minutes=travel_package_place.spending_time)
            if travel_package_place.in_return:
                travel_package_id_wise_return_places[travel_package_place.travel_package_id].append(
                    {
                        "place": place_id_wise_details[travel_package_place.place_id],
                        "order": travel_package_place.order,
                        "duration_to_reach": travel_package_place.duration_to_reach,
                        "spending_time": travel_package_place.spending_time,
                        "arrival_time": arrival_time,
                        "departure_time": departure_time,
                    }
                )
            else:
                travel_package_id_wise_forward_places[travel_package_place.travel_package_id].append(
                    {
                        "place": place_id_wise_details[travel_package_place.place_id],
                        "order": travel_package_place.order,
                        "duration_to_reach": travel_package_place.duration_to_reach,
                        "spending_time": travel_package_place.spending_time,
                        "arrival_time": arrival_time,
                        "departure_time": departure_time,
                    }
                )
            start_time = departure_time

        return travel_package_id_wise_forward_places, travel_package_id_wise_return_places

    @staticmethod
    def get_travel_package_id_wise_images(travel_package_ids):
        travel_package_images = TravelPackageImage.objects.filter(travel_package_id__in=travel_package_ids)

        travel_package_id_wise_images = defaultdict(list)
        for travel_package_image in travel_package_images:
            image_url = travel_package_image.image.url
            image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
            travel_package_id_wise_images[travel_package_image.travel_package_id].append(
                {
                    "id": travel_package_image.id,
                    "image": image_url,
                    "order": travel_package_image.order
                }
            )
        return travel_package_id_wise_images

    @staticmethod
    def get_travel_package_id_wise_places_count(travel_package_ids):
        travel_package_places_count = PackagePlaces.objects.filter(travel_package_id__in=travel_package_ids) \
            .values('travel_package').annotate(count=Count('id')).values('travel_package_id', 'count')

        travel_package_id_wise_places_count = defaultdict(int)
        for travel_package_place_count in travel_package_places_count:
            travel_package_id_wise_places_count[travel_package_place_count["travel_package_id"]] = \
                travel_package_place_count["count"]

        return travel_package_id_wise_places_count

    def get(self, travel_package_id, request):
        start_time = request.data["start_time"]
        self.travel_package_object = TravelPackage.objects.get(product_id=travel_package_id)
        self.initialize_product_class(None)
        start_time = datetime.strptime(start_time, settings.DATE_FORMAT)

        travel_package_data = self.travel_package_serializer.data

        travel_package_id_wise_forward_places, travel_package_id_wise_return_places \
            = self.get_travel_package_id_wise_places_details([self.travel_package_object.id], start_time)

        forward_places = travel_package_id_wise_forward_places[self.travel_package_object.id]
        return_places = travel_package_id_wise_return_places[self.travel_package_object.id]
        travel_package_data["places"] = {
            "count": len(forward_places) + len(return_places),
            "forward": forward_places,
            "return": return_places
        }

        travel_package_id_wise_images_dict = self.get_travel_package_id_wise_images([self.travel_package_object.id])
        travel_package_data["images"] = travel_package_id_wise_images_dict[self.travel_package_object.id]

        return travel_package_data

    def get_by_ids(self, travel_package_ids):
        travel_packages = TravelPackage.objects.filter(id__in=travel_package_ids)

        travel_package_serializer = TravelPackageSerializer(travel_packages, many=True)
        travel_packages_data = travel_package_serializer.data

        travel_package_id_wise_images_dict = self.get_travel_package_id_wise_images(travel_package_ids)
        travel_package_id_wise_places_count = self.get_travel_package_id_wise_places_count(travel_package_ids)
        travel_package_id_wise_vehicles_count = get_travel_package_id_wise_vehicles_count(travel_package_ids)
        for travel_package_data in travel_packages_data:
            travel_package_data["places_count"] = travel_package_id_wise_places_count[travel_package_data["id"]]
            travel_package_data["vehicles_count"] = travel_package_id_wise_vehicles_count[travel_package_data["id"]]
            travel_package_data["images"] = travel_package_id_wise_images_dict[travel_package_data["id"]]

        return travel_packages_data

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
