from Product.product_interface import ProductInterface
from .serializers import HireAVehicleSerializer, HireAVehicleDistancePriceSerializer
from typing import Dict
from collections import defaultdict
from .models import HireAVehicle, HireAVehicleDistancePrice
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details, get_basic_driver_data_by_id, \
    get_basic_driver_id_wise_details, check_driver_exists_by_id, check_vehicle_exists_by_id
from .constants import DurationType, TripType


def get_distance_price_data(hire_a_vehicle_ids):
    distance_price = HireAVehicleDistancePrice.objects.filter(hire_a_vehicle__in=hire_a_vehicle_ids)
    distance_price_serializer = HireAVehicleDistancePriceSerializer(distance_price, many=True)

    return distance_price_serializer.data


class HireAVehicleView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.hire_a_vehicle_serializer = None
        self.hire_a_vehicle_object = None
        self.distance_price_data = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, hire_a_vehicle_data):
        if hire_a_vehicle_data:
            self.distance_price_data = hire_a_vehicle_data.pop("distance_price", [])

        hire_a_vehicle_object_defined = self.hire_a_vehicle_object is not None
        hire_a_vehicle_data_defined = hire_a_vehicle_data is not None

        # for update
        if hire_a_vehicle_object_defined and hire_a_vehicle_data_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(
                self.hire_a_vehicle_object, data=hire_a_vehicle_data)
        # for create
        elif hire_a_vehicle_data_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(data=hire_a_vehicle_data)
        # for get
        elif hire_a_vehicle_object_defined:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer(self.hire_a_vehicle_object)
        else:
            self.hire_a_vehicle_serializer = HireAVehicleSerializer()

    def validate_create_data(self, hire_a_vehicle_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(hire_a_vehicle_data)

        vehicle = hire_a_vehicle_data["vehicle"]
        default_driver = hire_a_vehicle_data["default_driver"]

        if not check_driver_exists_by_id(default_driver):
            is_valid = False
            errors['default_driver'] = "Default driver does not exist"

        if not check_vehicle_exists_by_id(vehicle):
            is_valid = False
            errors['vehicle'] = "Vehicle does not exist"
            return is_valid, errors

        hire_a_vehicle_data_valid = self.hire_a_vehicle_serializer.is_valid()
        if not hire_a_vehicle_data_valid:
            is_valid = False
            errors.update(self.hire_a_vehicle_serializer.errors)

        distance_price_serializer = HireAVehicleDistancePriceSerializer(
            data=self.distance_price_data, many=True)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        return is_valid, errors

    def create(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string,
            "distance_price": [
                    {
                        'duration_type' : string,
                        'km_limit': int,
                        'km_price': int,
                        'excess_km_price':int,
                        'excess_duration_price': int,
                        'is_infinity': Boolean,
                        'single_trip_return_value_per_km' : int,
                        'min_time_duration': int,
                        'max_time_duration': int,
                    },
                    {
                        'duration_type' : string,
                        'km_limit': int,
                        'km_price': int,
                        'excess_km_price':int,
                        'excess_duration_price': int,
                        'is_infinity': Boolean,
                        'single_trip_return_value_per_km' : int,
                        'min_time_duration': int,
                        'max_time_duration': int,
                    }
                ]
        }
        """

        hire_a_vehicle_object = self.hire_a_vehicle_serializer.create(hire_a_vehicle_data)

        for distance_price in self.distance_price_data:
            distance_price["hire_a_vehicle"] = hire_a_vehicle_object
            if 'is_infinity' in distance_price:
                distance_price['excess_km_price'] = 0 if distance_price['is_infinity'] else distance_price['excess_km_price']
            else:
                distance_price['is_infinity'] = False

        distance_price_serializer = HireAVehicleDistancePriceSerializer()
        distance_price_serializer.bulk_create(self.distance_price_data)

        return {
            "id": hire_a_vehicle_object.id
        }

    def validate_update_data(self, hire_a_vehicle_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.hire_a_vehicle_object \
                = HireAVehicle.objects.get(product_id=hire_a_vehicle_data["product"])
        except HireAVehicle.DoesNotExist:
            return False, {"errors": "Hotel A Vehicle does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(hire_a_vehicle_data)

        hire_a_vehicle_data_valid = self.hire_a_vehicle_serializer.is_valid()
        if not hire_a_vehicle_data_valid:
            is_valid = False
            errors.update(self.hire_a_vehicle_serializer.errors)

        distance_price_serializer = HireAVehicleDistancePriceSerializer(
            data=self.distance_price_data)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        return is_valid, errors

    def update(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string,
            "distance_price": [
                {
                    'id' : string,
                    'duration_type' : string,
                    'km_limit': int,
                    'km_price': int,
                    'excess_km_price':int,
                    'excess_duration_price': int,
                    'is_infinity': Boolean,
                    'single_trip_return_value_per_km' : int,
                    'min_time_duration': int,
                    'max_time_duration': int,
                }
            ]
        }
        """

        self.hire_a_vehicle_serializer.update(self.hire_a_vehicle_object, hire_a_vehicle_data)
        distance_price_serializer = HireAVehicleDistancePrice.objects.filter(id=self.distance_price_data[0]["id"])
        distance_price_serializer.update(self.distance_price_data[0])

    def get(self, product_id):
        self.hire_a_vehicle_object = HireAVehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        hire_a_vehicle_data = self.hire_a_vehicle_serializer.data
        vehicle_data = get_vehicle_data_by_id(hire_a_vehicle_data["vehicle"])
        hire_a_vehicle_data["vehicle"] = vehicle_data
        driver_data = get_basic_driver_data_by_id(hire_a_vehicle_data["default_driver"])
        hire_a_vehicle_data["default_driver"] = driver_data
        hire_a_vehicle_data['distance_price'] = get_distance_price_data([self.hire_a_vehicle_object.id])
        return hire_a_vehicle_data

    def get_by_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)

        hire_a_vehicle_serializer = HireAVehicleSerializer(hire_a_vehicles, many=True)
        hire_a_vehicles_data = hire_a_vehicle_serializer.data

        hire_a_vehicles_ids = list(map(lambda x: x['id'], hire_a_vehicles_data))
        all_distance_prices = get_distance_price_data(hire_a_vehicles_ids)

        hire_a_vehicle_id_wise_distance_prices = defaultdict(list)
        for distance_price in all_distance_prices:
            hire_a_vehicle_id_wise_distance_prices[distance_price['hire_a_vehicle']].append(distance_price)

        vehicle_ids = []
        for hire_a_vehicle_data in hire_a_vehicles_data:
            vehicle_ids.append(hire_a_vehicle_data["vehicle"])

        driver_ids = []
        for hire_a_vehicle_data in hire_a_vehicles_data:
            driver_ids.append(hire_a_vehicle_data["default_driver"])

        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        driver_id_wise_details = get_basic_driver_id_wise_details(driver_ids)
        for hire_a_vehicle_data in hire_a_vehicles_data:
            hire_a_vehicle_data["vehicle"] = vehicle_id_wise_details[hire_a_vehicle_data["vehicle"]]
            hire_a_vehicle_data["default_driver"] = driver_id_wise_details[hire_a_vehicle_data["default_driver"]]
            hire_a_vehicle_data['distance_price'] = hire_a_vehicle_id_wise_distance_prices[hire_a_vehicle_data["id"]]

        return hire_a_vehicles_data

    def get_sub_products_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_data = defaultdict(dict)
        hire_a_vehicles_sub_products_ids = defaultdict(list)
        hire_a_vehicle_product_details = defaultdict()
        hire_a_vehicles_ids = []

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_ids.append(each_hire_a_vehicle.id)

        hire_a_vehicle_distance_price_data = HireAVehicleDistancePrice.objects \
                                                .filter(hire_a_vehicle__in = hire_a_vehicles_ids)
        hire_a_vehicle_distance_price_serializer = \
            HireAVehicleDistancePriceSerializer(hire_a_vehicle_distance_price_data, many=True)
        for each_distance_price in hire_a_vehicle_distance_price_serializer.data:
            hire_a_vehicles_data[each_distance_price["hire_a_vehicle"]] \
                .update({each_distance_price["duration_type"]: each_distance_price})

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_sub_products_ids[each_hire_a_vehicle.product_id] = \
                [ each_hire_a_vehicle.vehicle_id, each_hire_a_vehicle.default_driver_id ]
            hire_a_vehicle_product_details[each_hire_a_vehicle.product_id] = \
                hire_a_vehicles_data[each_hire_a_vehicle.id]
            
        return hire_a_vehicles_sub_products_ids, hire_a_vehicle_product_details

    def get_transport_price_data(self, product_ids, product_ids_with_duration):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_data = defaultdict(dict)
        hire_a_vehicle_price_data = defaultdict()
        hire_a_vehicles_ids = []

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_ids.append(each_hire_a_vehicle.id)

        hire_a_vehicle_distance_price_data = HireAVehicleDistancePrice.objects \
            .filter(hire_a_vehicle__in=hire_a_vehicles_ids)

        for each_distance_price in hire_a_vehicle_distance_price_data:
            hire_a_vehicles_data[each_distance_price.hire_a_vehicle.product_id]\
                .update({each_distance_price.duration_type:each_distance_price})

        for each_hire_a_vehicle in hire_a_vehicles:
            total_hours = product_ids_with_duration[each_hire_a_vehicle.product_id]["duration"]
            trip_type = product_ids_with_duration[each_hire_a_vehicle.product_id]["trip_type"]
            excess_duration = product_ids_with_duration[each_hire_a_vehicle.product_id]["excess_duration"]
            excess_km = product_ids_with_duration[each_hire_a_vehicle.product_id]["excess_km"]
            days = total_hours // 24
            hours = total_hours % 24
            total_price = duration_price = trip_type_price = excess_km_price = excess_duration_price = 0

            day_data = hire_a_vehicles_data[each_hire_a_vehicle.product_id][DurationType.day.value]
            hour_data = hire_a_vehicles_data[each_hire_a_vehicle.product_id][DurationType.hour.value]

            duration_price = day_data.km_price * day_data.km_limit * days + hour_data.km_price * hour_data.km_limit * hours

            if trip_type == TripType.single.value:
                trip_type_price = day_data.single_trip_return_value_per_km * day_data.km_limit * days + \
                               hour_data.single_trip_return_value_per_km * hour_data.km_limit * hours
            if excess_km > 0:
                if days == 0:
                    excess_km_price = hour_data.excess_km_price * excess_km
                else:
                    excess_km_price = day_data.excess_km_price * excess_km

            if excess_duration > 0:
                excess_days = excess_duration // 24
                excess_hours = excess_duration % 24

                excess_duration_price = day_data.excess_duration_price * excess_days + \
                               hour_data.excess_duration_price * excess_hours

            total_price = duration_price + trip_type_price + excess_duration_price + excess_km_price

            hire_a_vehicle_price_data[each_hire_a_vehicle.product_id] = {
                "duration_price": duration_price,
                "trip_type_price": trip_type_price,
                "excess_duration_price": excess_duration_price,
                "excess_km_price": excess_km_price,
                "total_price": total_price
            }

        return hire_a_vehicle_price_data






