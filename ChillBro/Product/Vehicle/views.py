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


def get_vehicle_type_id_wise_characteristics(vehicle_type_ids):
    vehicle_type_characteristics = \
        VehicleTypeCharacteristics.objects.select_related('vehicle_characteristic')\
        .filter(vehicle_type__in=vehicle_type_ids)

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


def add_characteristics_for_vehicle_types(vehicle_types_data):
    vehicle_type_ids = []
    for vehicle_type in vehicle_types_data:
        vehicle_type_ids.append(vehicle_type["id"])

    vehicle_type_id_wise_characteristics_dict = get_vehicle_type_id_wise_characteristics(vehicle_type_ids)
    for vehicle_type in vehicle_types_data:
        vehicle_type["characteristics"] = vehicle_type_id_wise_characteristics_dict[vehicle_type["id"]]


class VehicleTypeList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        add_characteristics_for_vehicle_types(response.data["results"])
        return response

    @staticmethod
    def validate_create_data(vehicle_type_data):
        is_valid = True
        errors = defaultdict(list)

        vehicle_type_serializer = VehicleTypeSerializer(data=vehicle_type_data)
        if not vehicle_type_serializer.is_valid():
            is_valid = False
            errors["vehicle_type"].append(vehicle_type_serializer.errors)

        characteristics = vehicle_type_data["characteristics"]
        vehicle_characteristic_ids = []
        for characteristic in characteristics:
            vehicle_characteristic_ids.append(characteristic["vehicle_characteristic"])

        vehicle_characteristic_ids_valid, invalid_vehicle_characteristic_ids = \
            validate_vehicle_characteristic_ids(vehicle_characteristic_ids)
        if not vehicle_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_characteristic_ids"].append(invalid_vehicle_characteristic_ids)

        vehicle_type_characteristic_serializer = VehicleTypeCharacteristicsSerializer(
            data=characteristics, many=True)
        if not vehicle_type_characteristic_serializer.is_valid():
            is_valid = False
            errors["characteristics"].append(vehicle_type_characteristic_serializer.errors)

        return is_valid, errors

    def post(self, request, *args, **kwargs):
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
        request_data = request.data.dict()

        # remove when not using postman
        characteristics = request_data["characteristics"]
        request_data["characteristics"] = json.loads(characteristics)

        is_valid, errors = self.validate_create_data(request_data)
        if not is_valid:
            return Response({"message": "Vehicle Type can't be created", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        characteristics = request_data.pop("characteristics", None)

        vehicle_type_serializer = VehicleTypeSerializer()
        vehicle_type = vehicle_type_serializer.create(request_data)

        for characteristic in characteristics:
            characteristic["vehicle_type"] = vehicle_type.id
        vehicle_type_characteristic_serializer = VehicleTypeCharacteristicsSerializer()
        vehicle_type_characteristic_serializer.bulk_create(characteristics)

        return Response({"message": "Vehicle Type created successfully"},
                        status=status.HTTP_200_OK)


class VehicleTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        add_characteristics_for_vehicle_types([response.data])
        return response

    @staticmethod
    def validate_update_data(vehicle_type_obj, vehicle_type_data):
        is_valid = True
        errors = defaultdict(list)

        vehicle_type_serializer = VehicleTypeSerializer(vehicle_type_obj, data=vehicle_type_data)
        if not vehicle_type_serializer.is_valid():
            is_valid = False
            errors.update(vehicle_type_serializer.errors)

        characteristics = vehicle_type_data["characteristics"]
        vehicle_type_characteristics_update_serializer = VehicleTypeCharacteristicsUpdateSerializer(
            data=characteristics)
        if not vehicle_type_characteristics_update_serializer.is_valid():
            is_valid = False
            errors.update(vehicle_type_characteristics_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        vehicle_characteristic_ids = []
        vehicle_type_characteristic_ids = []
        for vehicle_type_characteristic in characteristics["add"]:
            vehicle_type_characteristics_exists = VehicleTypeCharacteristics.objects\
                .filter(vehicle_type=vehicle_type_obj,
                        vehicle_characteristic_id=vehicle_type_characteristic["vehicle_characteristic"]).exists()
            if vehicle_type_characteristics_exists:
                is_valid = False
                errors["VehicleType-Characteristic"].append(
                    "VehicleType-{0}, Characteristic-{1}: Already Exists!"
                    .format(vehicle_type_obj, vehicle_type_characteristic["vehicle_characteristic"]))

            vehicle_type_characteristic["vehicle_type"] = vehicle_type_obj.id
            vehicle_characteristic_ids.append(vehicle_type_characteristic["vehicle_characteristic"])

        for vehicle_type_characteristic in characteristics["change"]:
            vehicle_type_characteristic_ids.append(vehicle_type_characteristic["id"])

        for vehicle_type_characteristic in characteristics["delete"]:
            vehicle_type_characteristic_ids.append(vehicle_type_characteristic["id"])

        vehicle_characteristic_ids_valid, invalid_vehicle_characteristic_ids = \
            validate_vehicle_characteristic_ids(vehicle_characteristic_ids)
        if not vehicle_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_characteristic_ids"] = invalid_vehicle_characteristic_ids

        vehicle_type_characteristic_ids_valid, invalid_vehicle_type_characteristic_ids \
            = validate_vehicle_type_characteristic_ids(vehicle_type_obj.id, vehicle_type_characteristic_ids)
        if not vehicle_type_characteristic_ids_valid:
            is_valid = False
            errors["invalid_vehicle_type_characteristic_ids"] = invalid_vehicle_type_characteristic_ids

        return is_valid, errors

    def put(self, request, *args, **kwargs):
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

        try:
            vehicle_type_obj \
                = VehicleType.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return Response({"message": "Vehicle Type can't be updated", "errors": "Invalid Vehicle Type Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        request_data = request.data.dict()

        # remove when not using postman
        characteristics = request_data["characteristics"]
        request_data["characteristics"] = json.loads(characteristics)
        characteristics = request_data["characteristics"]

        is_valid, errors = self.validate_update_data(vehicle_type_obj, request_data)
        if not is_valid:
            return Response({"message": "Vehicle Type can't be updated", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        vehicle_type_serializer = VehicleTypeSerializer()
        vehicle_type_serializer.update(vehicle_type_obj, request_data)

        vehicle_type_characteristics_serializer = VehicleTypeCharacteristicsSerializer()
        vehicle_type_characteristics_serializer.bulk_create(characteristics["add"])
        vehicle_type_characteristics_serializer.bulk_update(characteristics["change"])
        vehicle_type_characteristics_serializer.bulk_delete(characteristics["delete"])

        return Response({"message": "Vehicle Type updated successfully"},
                        status=status.HTTP_200_OK)
