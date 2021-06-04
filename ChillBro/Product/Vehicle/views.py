import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import VehicleType, VehicleCharacteristics, VehicleTypeCharacteristics
from .serializers import VehicleTypeSerializer, VehicleCharacteristicsSerializer, VehicleTypeCharacteristicsSerializer, \
    VehicleTypeCharacteristicsUpdateSerializer
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from collections import defaultdict
from rest_framework.response import Response
from ..product_interface import ProductInterface
from typing import Dict


class VehicleCharacteristicsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleCharacteristics.objects.all()
    serializer_class = VehicleCharacteristicsSerializer


class VehicleCharacteristicsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleCharacteristics.objects.all()
    serializer_class = VehicleCharacteristicsSerializer


def validate_vehicle_characteristic_ids(vehicle_characteristic_ids):
    existing_characteristics = VehicleCharacteristics.objects.filter(id__in=vehicle_characteristic_ids)\
        .values_list('id', flat=True)
    if len(existing_characteristics) != len(vehicle_characteristic_ids):
        return False, set(vehicle_characteristic_ids) - set(existing_characteristics)
    return True, []


def validate_vehicle_type_characteristic_ids(vehicle_type_id, vehicle_characteristic_type_ids):
    existing_vehicle_characteristic_type_ids \
        = VehicleTypeCharacteristics.objects.filter(
            id__in=vehicle_characteristic_type_ids, vehicle_type_id=vehicle_type_id)\
            .values_list('id', flat=True)

    if len(existing_vehicle_characteristic_type_ids) != len(vehicle_characteristic_type_ids):
        return False, set(vehicle_characteristic_type_ids) - set(existing_vehicle_characteristic_type_ids)
    return True, []


def get_vehicle_type_id_wise_characteristics(vehicle_type_ids, only_display_front=False):
    vehicle_type_characteristics = \
        VehicleTypeCharacteristics.objects.select_related('vehicle_characteristic')\
        .filter(vehicle_type__in=vehicle_type_ids)
    if only_display_front:
        vehicle_type_characteristics = vehicle_type_characteristics.filter(
            vehicle_characteristic__display_front=True)

    vehicle_type_id_wise_characteristics_dict = defaultdict(list)
    for vehicle_type_characteristic in vehicle_type_characteristics:
        icon_url = vehicle_type_characteristic.vehicle_characteristic.icon_url
        icon_url = icon_url.url.replace(settings.IMAGE_REPLACED_STRING, "")

        vehicle_type_id_wise_characteristics_dict[vehicle_type_characteristic.vehicle_type_id].append(
            {
                "name": vehicle_type_characteristic.vehicle_characteristic.name,
                "icon_url": icon_url,
                "units": vehicle_type_characteristic.vehicle_characteristic.units,
                "value": vehicle_type_characteristic.value
            }
        )

    return vehicle_type_id_wise_characteristics_dict


def add_characteristics_for_vehicle_types(vehicle_types_data, only_display_front=False):
    vehicle_type_ids = []
    for vehicle_type in vehicle_types_data:
        vehicle_type_ids.append(vehicle_type["id"])

    vehicle_type_id_wise_characteristics_dict = get_vehicle_type_id_wise_characteristics(
        vehicle_type_ids, only_display_front)
    for vehicle_type in vehicle_types_data:
        vehicle_type["characteristics"] = vehicle_type_id_wise_characteristics_dict[vehicle_type["id"]]


class VehicleTypeView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.vehicle_type_serializer = None
        self.characteristics_data = None

        self.vehicle_type_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, vehicle_type_data):
        if vehicle_type_data:
            self.characteristics_data = vehicle_type_data.pop("characteristics", [])

        vehicle_type_object_defined = self.vehicle_type_object is not None
        vehicle_type_data_defined = vehicle_type_data is not None

        # for update
        if vehicle_type_object_defined and vehicle_type_data_defined:
            self.vehicle_type_serializer = VehicleTypeSerializer(self.vehicle_type_object, data=vehicle_type_data)
        # for create
        elif vehicle_type_data_defined:
            self.vehicle_type_serializer = VehicleTypeSerializer(data=vehicle_type_data)
        # for get
        elif vehicle_type_object_defined:
            self.vehicle_type_serializer = VehicleTypeSerializer(self.vehicle_type_object)
        else:
            self.vehicle_type_serializer = VehicleTypeSerializer()

    def validate_create_data(self, vehicle_type_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(vehicle_type_data)

        if not self.vehicle_type_serializer.is_valid():
            is_valid = False
            errors["vehicle_type"].append(self.vehicle_type_serializer.errors)

        vehicle_characteristic_ids = []
        for characteristic in self.characteristics_data:
            vehicle_characteristic_ids.append(characteristic["vehicle_characteristic"])

        vehicle_characteristic_ids_valid, invalid_vehicle_characteristic_ids = \
            validate_vehicle_characteristic_ids(vehicle_characteristic_ids)
        if not vehicle_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_characteristic_ids"].append(invalid_vehicle_characteristic_ids)

        vehicle_type_characteristic_serializer = VehicleTypeCharacteristicsSerializer(
            data=self.characteristics_data, many=True)
        if not vehicle_type_characteristic_serializer.is_valid():
            is_valid = False
            errors["characteristics"].append(vehicle_type_characteristic_serializer.errors)

        return is_valid, errors

    def create(self, vehicle_type_data):
        """
            {
                name: string,
                description: string,
                category: id-string,
                category_product: id-string,
                no_of_people: int,
                wheel_type: string,
                icon_url: image,
                characteristics: [
                    {
                        'vehicle_characteristic': int,
                        'value': string
                    }
                ]
            }
        """

        vehicle_type_object = self.vehicle_type_serializer.create(vehicle_type_data)

        for characteristic in self.characteristics_data:
            characteristic["vehicle_type"] = vehicle_type_object.id
        vehicle_type_characteristic_serializer = VehicleTypeCharacteristicsSerializer()
        vehicle_type_characteristic_serializer.bulk_create(self.characteristics_data)

        return {
            "id": vehicle_type_object.id
        }

    def validate_update_data(self, vehicle_type_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of vehicle to be updated
        try:
            self.vehicle_type_object \
                = VehicleType.objects.get(id=vehicle_type_data["id"])
        except ObjectDoesNotExist:
            return False, {"errors": "Vehicle Type does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(vehicle_type_data)

        if not self.vehicle_type_serializer.is_valid():
            is_valid = False
            errors.update(self.vehicle_type_serializer.errors)

        vehicle_type_characteristics_update_serializer = VehicleTypeCharacteristicsUpdateSerializer(
            data=self.characteristics_data)
        if not vehicle_type_characteristics_update_serializer.is_valid():
            is_valid = False
            errors.update(vehicle_type_characteristics_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        vehicle_characteristic_ids = []
        vehicle_type_characteristic_ids = []
        for vehicle_type_characteristic in self.characteristics_data["add"]:
            vehicle_type_characteristics_exists = VehicleTypeCharacteristics.objects \
                .filter(vehicle_type=self.vehicle_type_object,
                        vehicle_characteristic_id=vehicle_type_characteristic["vehicle_characteristic"]).exists()
            if vehicle_type_characteristics_exists:
                is_valid = False
                errors["VehicleType-Characteristic"].append(
                    "VehicleType-{0}, Characteristic-{1}: Already Exists!"
                    .format(self.vehicle_type_object, vehicle_type_characteristic["vehicle_characteristic"]))

            vehicle_type_characteristic["vehicle_type"] = self.vehicle_type_object.id
            vehicle_characteristic_ids.append(vehicle_type_characteristic["vehicle_characteristic"])

        for vehicle_type_characteristic in self.characteristics_data["change"]:
            vehicle_type_characteristic_ids.append(vehicle_type_characteristic["id"])

        for vehicle_type_characteristic in self.characteristics_data["delete"]:
            vehicle_type_characteristic_ids.append(vehicle_type_characteristic["id"])

        vehicle_characteristic_ids_valid, invalid_vehicle_characteristic_ids = \
            validate_vehicle_characteristic_ids(vehicle_characteristic_ids)
        if not vehicle_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_characteristic_ids"] = invalid_vehicle_characteristic_ids

        vehicle_type_characteristic_ids_valid, invalid_vehicle_type_characteristic_ids \
            = validate_vehicle_type_characteristic_ids(
                self.characteristics_data.id, vehicle_type_characteristic_ids)
        if not vehicle_type_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_type_characteristic_ids"] = invalid_vehicle_type_characteristic_ids

        return is_valid, errors

    def update(self, vehicle_type_data):
        """
            {
                name: string,
                description: string,
                category: id-string,
                category_product: id-string,
                no_of_people: int,
                wheel_type: string,
                icon_url: image,
                characteristics: {
                    "add": [
                        {
                            'vehicle_characteristic': int,
                            'value': string
                        }
                    ],
                    "change": [
                        {
                            'id': string,
                            'value': string
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

        self.vehicle_type_serializer.update(self.vehicle_type_object, vehicle_type_data)

        vehicle_type_characteristics_serializer = VehicleTypeCharacteristicsSerializer()
        vehicle_type_characteristics_serializer.bulk_create(self.characteristics_data["add"])
        vehicle_type_characteristics_serializer.bulk_update(self.characteristics_data["change"])
        vehicle_type_characteristics_serializer.bulk_delete(self.characteristics_data["delete"])

    def get(self, vehicle_type_id):
        self.vehicle_type_object = VehicleType.objects.get(id=vehicle_type_id)
        self.initialize_product_class(None)

        vehicle_type_data = self.vehicle_type_serializer.data
        add_characteristics_for_vehicle_types([vehicle_type_data])

        return vehicle_type_data

    def get_by_ids(self, vehicle_type_ids):
        vehicle_types = VehicleType.objects.filter(id__in=vehicle_type_ids)

        vehicle_type_serializer = VehicleTypeSerializer(vehicle_types, many=True)
        vehicle_types_data = vehicle_type_serializer.data
        add_characteristics_for_vehicle_types(vehicle_types_data)

        return vehicle_types_data


class VehicleTypeList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    vehicle_type_view = VehicleTypeView()

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)

        vehicle_type_ids = []
        for vehicle_type in response.data["results"]:
            vehicle_type_ids.append(vehicle_type["id"])
        response.data["results"] = self.vehicle_type_view.get_by_ids(vehicle_type_ids)

        return response

    def post(self, request, *args, **kwargs):
        # TODO: remove when not using postman
        request_data = request.data.dict()
        characteristics = request_data["characteristics"]
        request_data["characteristics"] = json.loads(characteristics)

        is_valid, errors = self.vehicle_type_view.validate_create_data(request.data)
        if not is_valid:
            return Response({"message": "Can't create vehicle type", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        response_data = self.vehicle_type_view.create(request.data)
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class VehicleTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    vehicle_type_view = VehicleTypeView()

    def get(self, request, *args, **kwargs):
        try:
            response_data = self.vehicle_type_view.get(kwargs["id"])
        except ObjectDoesNotExist:
            return Response({"errors": "Product does not Exist!!!"}, 400)

        return Response(data=response_data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # TODO: remove when not using postman
        request_data = request.data.dict()
        characteristics = request_data["characteristics"]
        request_data["characteristics"] = json.loads(characteristics)
        request_data["id"] = id

        is_valid, errors = self.vehicle_type_view.validate_update_data(request_data)
        if not is_valid:
            return Response({"message": "Vehicle Type can't be updated", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        self.vehicle_type_view.update(request_data)
        return Response({"message": "Vehicle Type updated successfully"},
                        status=status.HTTP_200_OK)
