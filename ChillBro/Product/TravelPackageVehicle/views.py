from Product.product_interface import ProductInterface
from rest_framework.views import APIView
from .serializers import TravelPackageVehicleSerializer
from typing import Dict
from collections import defaultdict
from .models import TravelPackageVehicle
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class TravelPackageVehicleView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.travel_package_vehicle_serializer = None
        self.travel_package_vehicle_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, travel_package_vehicle_data):
        travel_package_vehicle_object_defined = self.travel_package_vehicle_object is not None
        travel_package_vehicle_data_defined = travel_package_vehicle_data is not None

        # for update
        if travel_package_vehicle_object_defined and travel_package_vehicle_data_defined:
            self.travel_package_vehicle_serializer = TravelPackageVehicleSerializer(
                self.travel_package_vehicle_object, data=travel_package_vehicle_data)
        # for create
        elif travel_package_vehicle_data_defined:
            self.travel_package_vehicle_serializer = TravelPackageVehicleSerializer(data=travel_package_vehicle_data)
        # for get
        elif travel_package_vehicle_object_defined:
            self.travel_package_vehicle_serializer = TravelPackageVehicleSerializer(self.travel_package_vehicle_object)
        else:
            self.travel_package_vehicle_serializer = TravelPackageVehicleSerializer()

    def validate_create_data(self, travel_package_vehicle_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(travel_package_vehicle_data)

        travel_package_vehicle_data_valid = self.travel_package_vehicle_serializer.is_valid()
        if not travel_package_vehicle_data_valid:
            is_valid = False
            errors.update(self.travel_package_vehicle_serializer.errors)

        return is_valid, errors

    def create(self, travel_package_vehicle_data):
        """
        travel_package_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "travel_package": string
        }
        """

        travel_package_vehicle_object = self.travel_package_vehicle_serializer.create(travel_package_vehicle_data)

        return {
            "id": travel_package_vehicle_object.id
        }

    def validate_update_data(self, travel_package_vehicle_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.travel_package_vehicle_object \
                = TravelPackageVehicle.objects.get(product_id=travel_package_vehicle_data["product"])
        except TravelPackageVehicle.DoesNotExist:
            return False, {"errors": "Travel Package Vehicle does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(travel_package_vehicle_data)

        travel_package_vehicle_data_valid = self.travel_package_vehicle_serializer.is_valid()
        if not travel_package_vehicle_data_valid:
            is_valid = False
            errors.update(self.travel_package_vehicle_serializer.errors)

        return is_valid, errors

    def update(self, travel_package_vehicle_data):
        """
        travel_package_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "travel_package": string
        }
        """

        self.travel_package_vehicle_serializer.update(self.travel_package_vehicle_object, travel_package_vehicle_data)

    def get(self, product_id):
        self.travel_package_vehicle_object = TravelPackageVehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        travel_package_vehicle_data = self.travel_package_vehicle_serializer.data
        vehicle_data = get_vehicle_data_by_id(travel_package_vehicle_data["vehicle"])
        travel_package_vehicle_data["vehicle"] = vehicle_data

        # NOTE: not adding travel package data as these details are not exposed directly

        return travel_package_vehicle_data

    def get_by_ids(self, product_ids):
        travel_package_vehicles = TravelPackageVehicle.objects.filter(product_id__in=product_ids)

        travel_package_vehicle_serializer = TravelPackageVehicleSerializer(travel_package_vehicles, many=True)
        travel_package_vehicles_data = travel_package_vehicle_serializer.data

        vehicle_ids = []
        for travel_package_vehicle_data in travel_package_vehicles_data:
            vehicle_ids.append(travel_package_vehicle_data["vehicle"])

        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        for travel_package_vehicle_data in travel_package_vehicles_data:
            travel_package_vehicle_data["vehicle"] = vehicle_id_wise_details[travel_package_vehicle_data["vehicle"]]

        return travel_package_vehicles_data


class TravelPackageVehiclesList(APIView):
    queryset = TravelPackageVehicle.objects.all()
    serializer_class = TravelPackageVehicleSerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    @staticmethod
    def update_vehicle_details(vehicle_details):
        vehicle_details.pop("features", None)
        vehicle_details.pop("type", None)
        vehicle_details.pop("featured", None)
        vehicle_details.pop("has_sizes", None)
        vehicle_details.pop("is_combo", None)
        vehicle_details.pop("category", None)
        vehicle_details.pop("category_product", None)
        vehicle_details.pop("images", None)
        vehicle_details.pop("combo_items", None)
        vehicle_details.pop("sizes", None)
        vehicle_details["travel_package_vehicle"].pop("id", None)
        vehicle_details["travel_package_vehicle"].pop("travel_package", None)
        vehicle_details["travel_package_vehicle"]["vehicle"].pop("id", None)

    def group_vehicle_details_by_vehicle_type(self, vehicles_details):
        vehicle_type_wise_vehicle_details = defaultdict(list)
        vehicle_type_wise_vehicle_type_details = defaultdict(dict)

        for vehicle_details in vehicles_details:
            vehicle_type_id = vehicle_details["travel_package_vehicle"]["vehicle"]["vehicle_type"]["id"]
            vehicle_type_details = vehicle_details["travel_package_vehicle"]["vehicle"].pop("vehicle_type", None)

            self.update_vehicle_details(vehicle_details)
            vehicle_type_wise_vehicle_details[vehicle_type_id].append(vehicle_details)
            vehicle_type_wise_vehicle_type_details[vehicle_type_id] = vehicle_type_details

        overall_grouped_data = []
        for vehicle_type_id in vehicle_type_wise_vehicle_type_details:
            vehicles = vehicle_type_wise_vehicle_details[vehicle_type_id]
            overall_grouped_data.append(
                {
                    "vehicle_type": vehicle_type_wise_vehicle_type_details[vehicle_type_id],
                    "vehicles_count": len(vehicles),
                    "vehicles": vehicles
                }
            )
        return overall_grouped_data

    def get(self, request, *args, **kwargs):
        from ..product_view import ProductView
        travel_package_id = kwargs["travel_package_id"]
        product_ids = TravelPackageVehicle.objects.filter(travel_package_id=travel_package_id)\
            .values_list('product_id', flat=True)

        product_details = ProductView().get_by_ids(product_ids)

        response_data = {
            "count": len(product_details),
            "results": self.group_vehicle_details_by_vehicle_type(product_details)
        }
        return Response(response_data, status=status.HTTP_200_OK)
