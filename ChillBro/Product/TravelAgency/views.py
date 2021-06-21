from Product.product_interface import ProductInterface
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from rest_framework import generics
from .serializers import TravelAgencySerializer, TravelAgencyPlacesSerializer, TravelAgencyImageSerializer, \
    TravelCharacteristicsSerializer, TravelAgencyCharacteristicsSerializer
from .models import TravelAgency, TravelAgencyPlaces, TravelAgencyImage, TravelCharacteristics, \
    TravelAgencyCharacteristics
from typing import Dict
from collections import defaultdict
from django.conf import settings
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .wrapper import get_place_id_wise_details, check_valid_place_ids


class TravelAgencyView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.travel_agency_serializer = None
        self.travel_agency_object = None

        self.travel_agency_images = []
        self.places_data = {}
        self.characteristics_data = {}

    # initialize the instance variables before accessing
    def initialize_product_class(self, travel_agency_data):
        travel_agency_object_defined = self.travel_agency_object is not None
        travel_agency_data_defined = travel_agency_data is not None

        if travel_agency_data_defined:
            if "images" in travel_agency_data:
                self.travel_agency_images = travel_agency_data.pop("images", [])
            if "places" in travel_agency_data:
                self.places_data = travel_agency_data.pop("places", [])
            if "characteristics" in travel_agency_data:
                self.characteristics_data = travel_agency_data.pop("characteristics", [])

        # for update
        if travel_agency_object_defined and travel_agency_data_defined:
            self.travel_agency_serializer = TravelAgencySerializer(
                self.travel_agency_object, data=travel_agency_data)
        # for create
        elif travel_agency_data_defined:
            self.travel_agency_serializer = TravelAgencySerializer(data=travel_agency_data)
        # for get
        elif travel_agency_object_defined:
            self.travel_agency_serializer = TravelAgencySerializer(self.travel_agency_object)
        else:
            self.travel_agency_serializer = TravelAgencySerializer()

    def validate_create_data(self, travel_agency_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(travel_agency_data)

        travel_agency_data_valid = self.travel_agency_serializer.is_valid()
        if not travel_agency_data_valid:
            is_valid = False
            errors.update(self.travel_agency_serializer.errors)

        # Validating places
        agency_places_serializer = TravelAgencyPlacesSerializer(data=self.places_data, many=True)
        if not agency_places_serializer.is_valid():
            is_valid = False
            errors["places"] = agency_places_serializer.errors
        # TODO: validate place ids

        # Validating images
        travel_agency_image_serializer = TravelAgencyImageSerializer(data=self.travel_agency_images, many=True)
        if not travel_agency_image_serializer.is_valid():
            is_valid = False
            errors["images"] = travel_agency_image_serializer.errors

        # Validating characteristics
        agency_characteristics_serializer = TravelAgencyCharacteristicsSerializer(data=self.characteristics_data,
                                                                                  many=True)
        if not agency_characteristics_serializer.is_valid():
            is_valid = False
            errors["characteristics"] = agency_characteristics_serializer.errors

        place_ids = list(map(lambda  x: x['place'],self.places_data))
        is_place_ids_valid, invalid_place_ids = check_valid_place_ids(place_ids)

        if not is_place_ids_valid:
            is_valid = False
            errors['incorrect place ids'] = invalid_place_ids
        return is_valid, errors

    def create(self, travel_agency_data):
        """
        {
            "product_id": string, # internal data need not be validated,
             "travel_agency":{
                duration_in_days: int,
                duration_in_nights: int,
                places: [
                    {
                        'place': string,
                        'order': int,
                        'type': string
                    }
                ],
                characteristics:[
                    {
                        "travel_characteristics": string
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

        travel_agency_object = self.travel_agency_serializer.create(travel_agency_data)

        # Add Places to Travel Agency
        for place_dict in self.places_data:
            place_dict["travel_agency"] = travel_agency_object.id
        TravelAgencyPlacesSerializer.bulk_create(self.places_data)

        # Add Images to Travel Agency
        for image_dict in self.travel_agency_images:
            image_dict["travel_agency"] = travel_agency_object.id
        TravelAgencyImageSerializer.bulk_create(self.travel_agency_images)

        # Add Characteristics to Travel Agency
        for characteristic_dict in self.characteristics_data:
            characteristic_dict["travel_agency"] = travel_agency_object.id
        TravelAgencyCharacteristicsSerializer.bulk_create(self.characteristics_data)

        return {
            "id": travel_agency_object.id
        }

    def validate_update_data(self, travel_agency_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.travel_agency_object \
                = TravelAgency.objects.get(id=travel_agency_data["id"])
        except TravelAgency.DoesNotExist:
            return False, {"errors": "Travel Agency does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(travel_agency_data)

        travel_agency_data_valid = self.travel_agency_serializer.is_valid()
        if not travel_agency_data_valid:
            is_valid = False
            errors.update(self.travel_agency_serializer.errors)

        # validate places for travel agency
        if self.places_data:
            if "add" in self.places_data:
                place_ids = []
                for travel_agency_place in self.places_data["add"]:
                    place_ids.append(travel_agency_place["place"])

                # TODO: validate place ids

                is_place_ids_valid, invalid_place_ids = check_valid_place_ids(place_ids)

                if not is_place_ids_valid:
                    is_valid = False
                    errors['incorrect place ids'] = invalid_place_ids
            # No validations required for delete

        return is_valid, errors

    def update(self, travel_agency_data):
        """
        {

            duration_in_days: int,
            duration_in_nights: int,
            'places': {
                'add': [
                    {
                        'place': string,
                        'order': int,
                        'type': string
                    },
                ],
                'delete': ['place_id']
            }
            "characteristics": {
                "add":[
                    {
                        "travel_characteristics": string
                    }
                ],
                "delete":[
                    characteristics_ids
                ]
            }
        }
        """

        self.travel_agency_serializer.update(self.travel_agency_object, travel_agency_data)

        # Add Places to Travel Agency
        travel_agency_places_add_dicts = []
        if "add" in self.places_data:
            for place_dict in self.places_data["add"]:
                travel_agency_place_dict = {
                    "travel_agency": self.travel_agency_object.id,
                    "place": place_dict["place"],
                    "type": place_dict["type"],
                    "order": place_dict["order"]
                }
                travel_agency_places_add_dicts.append(travel_agency_place_dict)
            TravelAgencyPlacesSerializer.bulk_create(travel_agency_places_add_dicts)

        # Deleting Places for Travel Agency
        if "delete" in self.places_data:
            delete_places = self.places_data["delete"]
            TravelAgencyPlacesSerializer.bulk_delete(self.travel_agency_object.id, delete_places)

        travel_agency_characteristics_add_dicts = []
        if "add" in self.characteristics_data:
            for characteristic_dict in self.characteristics_data["add"]:
                travel_agency_characteristic_dict = {
                    "travel_agency": self.travel_agency_object.id,
                    "travel_characteristic": characteristic_dict["travel_characteristic"],
                }
                travel_agency_characteristics_add_dicts.append(travel_agency_characteristic_dict)
            TravelAgencyCharacteristicsSerializer.bulk_create(travel_agency_places_add_dicts)

        # Deleting Characteristics for Travel Agency
        if "delete" in self.characteristics_data:
            delete_characteristics = self.characteristics_data["delete"]
            TravelAgencyCharacteristicsSerializer.bulk_delete(self.travel_agency_object.id, delete_characteristics)

    @staticmethod
    def get_travel_agency_id_wise_places_details(travel_agency_ids):
        travel_agency_places = TravelAgencyPlaces.objects.filter(travel_agency_id__in=travel_agency_ids)

        place_ids = []
        for travel_agency_place in travel_agency_places:
            place_ids.append(travel_agency_place.place_id)

        place_id_wise_details = get_place_id_wise_details(place_ids)

        travel_agency_id_wise_places = defaultdict(list)
        for travel_agency_place in travel_agency_places:
            travel_agency_id_wise_places[travel_agency_place.travel_agency_id].append(
                {
                    "place": place_id_wise_details[travel_agency_place.place_id],
                    "order": travel_agency_place.order,
                    "type": travel_agency_place.type
                }
            )

        return travel_agency_id_wise_places

    @staticmethod
    def get_travel_agency_id_wise_images(travel_agency_ids):
        travel_agency_images = TravelAgencyImage.objects.filter(travel_agency_id__in=travel_agency_ids)

        travel_agency_id_wise_images = defaultdict(list)
        for travel_agency_image in travel_agency_images:
            image_url = travel_agency_image.image.url
            image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
            travel_agency_id_wise_images[travel_agency_image.travel_agency_id].append(
                {
                    "id": travel_agency_image.id,
                    "image": image_url,
                    "order": travel_agency_image.order
                }
            )
        return travel_agency_id_wise_images

    @staticmethod
    def get_travel_agency_id_wise_places_count(travel_agency_ids):
        travel_agency_places_count = TravelAgencyPlaces.objects.filter(travel_agency_id__in=travel_agency_ids) \
            .values('travel_agency').annotate(count=Count('id')).values('travel_agency_id', 'count')

        travel_agency_id_wise_places_count = defaultdict(int)

        for travel_agency_place_count in travel_agency_places_count:
            travel_agency_id_wise_places_count[travel_agency_place_count["travel_agency_id"]] = \
                travel_agency_place_count["count"]

        return travel_agency_id_wise_places_count

    @staticmethod
    def get_travel_agency_id_wise_characteristics(travel_agency_ids):
        travel_agency_characteristics = TravelAgencyCharacteristics.objects.filter(
            travel_agency__in=travel_agency_ids).select_related('travel_characteristics')

        travel_agency_wise_characteristics = defaultdict(list)
        for travel_agency_characteristic in travel_agency_characteristics:
            icon_url = travel_agency_characteristic.travel_characteristics.icon_url.url
            icon_url = icon_url.replace(settings.IMAGE_REPLACED_STRING, "")
            travel_agency_wise_characteristics[travel_agency_characteristic.travel_agency_id].append(
                {
                    "name": travel_agency_characteristic.travel_characteristics.name,
                    "icon_url": icon_url
                }
            )

        return travel_agency_wise_characteristics

    def get(self, product_id):
        self.travel_agency_object = TravelAgency.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        travel_agency_data = self.travel_agency_serializer.data

        travel_agency_id_wise_places = self.get_travel_agency_id_wise_places_details([self.travel_agency_object.id])

        places = travel_agency_id_wise_places[self.travel_agency_object.id]
        travel_agency_data["places"] = places

        travel_agency_id_wise_images_dict = self.get_travel_agency_id_wise_images([self.travel_agency_object.id])
        travel_agency_data["images"] = travel_agency_id_wise_images_dict[self.travel_agency_object.id]

        travel_agency_id_wise_characteristics_dict = self.get_travel_agency_id_wise_characteristics(
            [self.travel_agency_object.id])
        travel_agency_data["characteristics"] = travel_agency_id_wise_characteristics_dict[self.travel_agency_object.id]

        return travel_agency_data

    def get_by_ids(self, travel_agency_ids):
        travel_agencys = TravelAgency.objects.filter(id__in=travel_agency_ids)

        travel_agency_serializer = TravelAgencySerializer(travel_agencys, many=True)
        travel_agencys_data = travel_agency_serializer.data

        travel_agency_id_wise_images_dict = self.get_travel_agency_id_wise_images(travel_agency_ids)
        travel_agency_id_wise_places = self.get_travel_agency_id_wise_places_details(travel_agency_ids)
        travel_agency_id_wise_characteristics_dict = self.get_travel_agency_id_wise_characteristics(travel_agency_ids)

        for travel_agency_data in travel_agencys_data:
            travel_agency_data["images"] = travel_agency_id_wise_images_dict[travel_agency_data["id"]]
            travel_agency_data['places'] = travel_agency_id_wise_places[travel_agency_data["id"]]
            travel_agency_data['characteristics'] = travel_agency_id_wise_characteristics_dict[travel_agency_data["id"]]

        return travel_agencys_data


class TravelCharacteristicsList(generics.ListCreateAPIView):
    permission_classes = (IsSuperAdminOrMYCEmployee,)
    queryset = TravelCharacteristics.objects.all()
    serializer_class = TravelCharacteristicsSerializer


class TravelCharacteristicsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsSuperAdminOrMYCEmployee,)
    queryset = TravelCharacteristics.objects.all()
    serializer_class = TravelCharacteristicsSerializer


class TravelAgencyImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = TravelAgencyImage.objects.all()
    serializer_class = TravelAgencyImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            travel_package = TravelAgency.objects.get(id=request.data['travel_package'])
        except ObjectDoesNotExist:
            return Response({"errors": "Travel Agency does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.create(request.data)
        return Response({"message": "Travel Agency Image added successfully"}, status=status.HTTP_201_CREATED)


class TravelAgencyImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = TravelAgencyImage.objects.all()
    serializer_class = TravelAgencyImageSerializer

    def delete(self, request, *args, **kwargs):
        try:
            travel_package_image = TravelAgencyImage.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"errors": "Travel Agency image does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)

        return super().delete(request, *args, **kwargs)
