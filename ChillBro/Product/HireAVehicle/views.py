from Product.product_interface import ProductInterface
from .serializers import HireAVehicleSerializer, HireAVehicleDistancePriceSerializer, \
    HireAVehicleDurationDetailsSerializer
from typing import Dict
from collections import defaultdict
from .models import HireAVehicle, HireAVehicleDistancePrice, HireAVehicleDurationDetails
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details, get_basic_driver_data_by_id, \
    get_basic_driver_id_wise_details, check_driver_exists_by_id, check_vehicle_exists_by_id
from .constants import DurationType, TripType
from ChillBro.helpers import get_date_format
from datetime import datetime
from math import ceil


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
        self.duration_details = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, hire_a_vehicle_data):
        if hire_a_vehicle_data:
            self.distance_price_data = hire_a_vehicle_data.pop("distance_price", [])
            self.duration_details = hire_a_vehicle_data.pop("duration_details", None)

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

        distance_price_serializer = HireAVehicleDistancePriceSerializer(data=self.distance_price_data)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        duration_details_serializer = HireAVehicleDurationDetailsSerializer(data=self.duration_details)
        if not duration_details_serializer.is_valid():
            is_valid = False
            errors["duration_details"].append(duration_details_serializer.errors)

        return is_valid, errors

    def create(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string,
            "distance_price":
                    {
                        'hour_price': int,
                        'day_price': int,
                        'is_km_infinity': Boolean,
                        'km_hour_limit': int,
                        'km_day_limit': int,
                        'excess_hour_duration_price': int,
                        'excess_day_duration_price': int,
                        'single_trip_return_value_per_km' : int,

                    },
            "duration_details":
                    {
                        'min_hour_duration': int,
                        'max_hour_duration': int,
                        'min_day_duration': int,
                        'max_day:duration': int,
                    }
        }
        """

        hire_a_vehicle_object = self.hire_a_vehicle_serializer.create(hire_a_vehicle_data)

        self.distance_price_data["hire_a_vehicle"] = hire_a_vehicle_object
        if 'is_infinity' in self.distance_price_data:
            self.distance_price_data['excess_km_price'] = 0 if self.distance_price_data['is_infinity'] else self.distance_price_data['excess_km_price']
        else:
            self.distance_price_data['is_infinity'] = False

        self.duration_details["hire_a_vehicle"] = hire_a_vehicle_object

        distance_price_serializer = HireAVehicleDistancePriceSerializer()
        distance_price_serializer.create(self.distance_price_data)

        duration_details_serializer = HireAVehicleDurationDetailsSerializer()
        duration_details_serializer.create(self.duration_details)

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

        distance_price_serializer = HireAVehicleDistancePriceSerializer(data=self.distance_price_data)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        duration_details_serializer = HireAVehicleDurationDetailsSerializer(data=self.duration_details)
        if not duration_details_serializer.is_valid():
            is_valid = False
            errors["duration_details"].append(duration_details_serializer.errors)

        return is_valid, errors

    def update(self, hire_a_vehicle_data):
        """
        hire_a_vehicle: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "default_driver": string,
            "distance_price":
                    {
                        'hour_price': int,
                        'day_price': int,
                        'excess_km_price':int,
                        'is_km_infinity': Boolean,
                        'km_hour_limit': int,
                        'km_day_limit': int,
                        'excess_hour_duration_price': int,
                        'excess_day_duration_price': int,
                        'single_trip_return_value_per_km' : int,

                    },
            "duration_details":
                    {
                        'min_hour_duration': int,
                        'max_hour_duration': int,
                        'min_day_duration': int,
                        'max_day:duration': int,
                    }
        }
        """

        self.hire_a_vehicle_serializer.update(self.hire_a_vehicle_object, hire_a_vehicle_data)
        distance_price_serializer = HireAVehicleDistancePrice.objects.filter(hire_a_vehicle=self.hire_a_vehicle_object)
        distance_price_serializer.update(self.distance_price_data)
        duration_details_serializer = HireAVehicleDurationDetails.objects.filter(hire_a_vehicle=self.hire_a_vehicle_object)
        duration_details_serializer.update(self.duration_details)

    def get(self, product_id):
        self.hire_a_vehicle_object = HireAVehicle.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        hire_a_vehicle_data = self.hire_a_vehicle_serializer.data
        vehicle_data = get_vehicle_data_by_id(hire_a_vehicle_data["vehicle"])
        hire_a_vehicle_data["vehicle"] = vehicle_data
        driver_data = get_basic_driver_data_by_id(hire_a_vehicle_data["default_driver"])
        hire_a_vehicle_data["default_driver"] = driver_data
        hire_a_vehicle_data['distance_price'] = self.get_price_data([product_id])[product_id]
        hire_a_vehicle_data['duration_details'] = self.get_duration_data([product_id])[product_id]

        return hire_a_vehicle_data

    def get_by_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)

        hire_a_vehicle_serializer = HireAVehicleSerializer(hire_a_vehicles, many=True)
        hire_a_vehicles_data = hire_a_vehicle_serializer.data

        hire_a_vehicle_id_wise_distance_prices = self.get_price_data(product_ids)
        hire_a_vehicle_id_wise_duration_details = self.get_duration_data(product_ids)

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
            hire_a_vehicle_data['distance_price'] = \
                hire_a_vehicle_id_wise_distance_prices[hire_a_vehicle_data["product"]]
            hire_a_vehicle_data['duration_details'] = \
                hire_a_vehicle_id_wise_duration_details[hire_a_vehicle_data["product"]]

        return hire_a_vehicles_data

    def get_sub_products_ids(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_sub_products_ids = defaultdict(list)

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_sub_products_ids[each_hire_a_vehicle.product_id] = \
                [ each_hire_a_vehicle.vehicle_id, each_hire_a_vehicle.default_driver_id ]

        return hire_a_vehicles_sub_products_ids

    def get_price_data(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_data = defaultdict()
        hire_a_vehicle_price_details = defaultdict()
        hire_a_vehicles_ids = []

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_ids.append(each_hire_a_vehicle.id)

        hire_a_vehicle_distance_price_data = HireAVehicleDistancePrice.objects \
                                                .filter(hire_a_vehicle__in = hire_a_vehicles_ids)
        hire_a_vehicle_distance_price_serializer = \
            HireAVehicleDistancePriceSerializer(hire_a_vehicle_distance_price_data, many=True)

        for each_distance_price in hire_a_vehicle_distance_price_serializer.data:
            hire_a_vehicles_data[each_distance_price["hire_a_vehicle"]] =each_distance_price

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicle_price_details[each_hire_a_vehicle.product_id] = \
                hire_a_vehicles_data[each_hire_a_vehicle.id]

        return hire_a_vehicle_price_details

    def get_duration_data(self, product_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_data = defaultdict()
        hire_a_vehicle_duration_details = defaultdict()
        hire_a_vehicles_ids = []

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicles_ids.append(each_hire_a_vehicle.id)

        hire_a_vehicle_duration_details_data = HireAVehicleDurationDetails.objects \
            .filter(hire_a_vehicle__in=hire_a_vehicles_ids)
        hire_a_vehicle_duration_details_serializer = \
            HireAVehicleDurationDetailsSerializer(hire_a_vehicle_duration_details_data, many=True)

        for each_duration_details in hire_a_vehicle_duration_details_serializer.data:
            hire_a_vehicles_data[each_duration_details["hire_a_vehicle"]] =each_duration_details

        for each_hire_a_vehicle in hire_a_vehicles:
            hire_a_vehicle_duration_details[each_hire_a_vehicle.product_id] = \
                hire_a_vehicles_data[each_hire_a_vehicle.id]

        return hire_a_vehicle_duration_details

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        hire_a_vehicles = HireAVehicle.objects.filter(product_id__in=product_ids)
        hire_a_vehicles_price_details = self.get_price_data(product_ids)
        result = defaultdict()

        # for each_hire_a_vehicle in hire_a_vehicles:
        #     hire_a_vehicles_ids.append(each_hire_a_vehicle.id)
        #
        # hire_a_vehicle_prices = HireAVehicleDistancePrice.objects.filter(hire_a_vehicle__in=hire_a_vehicles_ids)
        #
        # for each_price in hire_a_vehicle_prices:
        #     hire_a_vehicles_price_details[each_price.hire_a_vehicle.product_id] = each_price

        for each_hire_a_vehicle in hire_a_vehicles:
            each_hire_a_vehicle_details = product_details_with_ids[each_hire_a_vehicle.product_id]
            start_time_date_object = each_hire_a_vehicle_details['start_time']
            end_time_date_object = each_hire_a_vehicle_details['end_time']
            quantity = each_hire_a_vehicle_details["quantity"]
            trip_type = each_hire_a_vehicle_details["trip_type"]
            discount_percentage = each_hire_a_vehicle_details["discount_percentage"]

            difference_date = (end_time_date_object - start_time_date_object)
            total_hours = ceil((difference_date.total_seconds() // 60) / 60)
            days = total_hours // 24
            hours = total_hours % 24
            trip_type_price = 0

            price_data = hire_a_vehicles_price_details[each_hire_a_vehicle.product_id]

            duration_price = price_data.day_price * price_data.km_day_limit * days + \
                             price_data.hour_price  * price_data.km_hour_limit * hours

            if trip_type == TripType.single.value:
                trip_type_price = price_data.single_trip_return_value_per_km * (price_data.km_day_limit * days + \
                                price_data.km_hour_limit * hours)

            total_price = (duration_price + trip_type_price) * quantity
            discounted_price = total_price - ((total_price * discount_percentage) /100)

            result[each_hire_a_vehicle.product_id] = {
                "duration_price": duration_price,
                "trip_type_price": trip_type_price,
                "total_price": total_price,
                "discounted_price": discounted_price
            }

        return result

    def calculate_final_prices(self, products):
        final_prices = defaultdict()
        for each_product in products:
            price_data = products[each_product]["price_data"]
            start_time = datetime.strptime(products[each_product]["start_time"], get_date_format())
            booking_end_time = datetime.strptime(products[each_product]["booking_end_time"], get_date_format())
            present_end_time = datetime.strptime(products[each_product]["present_end_time"], get_date_format())
            booking_difference_date = (booking_end_time - start_time)
            booking_total_hours = ceil((booking_difference_date.total_seconds() // 60) / 60)
            days = booking_total_hours // 24
            hours = booking_total_hours % 24
            if present_end_time > booking_end_time:
                excess_difference_date = (present_end_time - booking_end_time)
                excess_total_hours = ceil((excess_difference_date.total_seconds() // 60) / 60)
                excess_days = excess_total_hours // 24
                excess_hours = excess_total_hours % 24
                excess_duration_price = price_data["excess_day_duration_price"] *excess_days + \
                                        price_data["excess_hour_duration_price"] * excess_hours
            else:
                excess_duration_price = 0
            max_km_can_travel = price_data["km_day_limit"] * days + price_data["km_hour_limit"] * hours
            km_travelled = price_data["booking_ending_km_value"] - price_data["booking_started_km_value"]
            if km_travelled > max_km_can_travel:
                excess_km_travelled = km_travelled - max_km_can_travel
                excess_km_price = price_data["excess_km_price"] * excess_km_travelled
            else:
                excess_km_price = 0

            duration_price = price_data["day_price"] * price_data["km_day_limit"] * days + \
                             price_data["hour_price"] * price_data["km_hour_limit"] * hours

            if price_data["trip_type"] == TripType.single.value:
                trip_type_price = price_data["single_trip_return_value_per_km"] * \
                                    (price_data["km_day_limit"] * days + price_data["km_hour_limit"] * hours)
            else:
                trip_type_price = 0

            total_price = (duration_price + trip_type_price + excess_km_price + excess_duration_price) * \
                          products[each_product]["quantity"]
            discounted_price = total_price - ((total_price * products[each_product]["discount_percentage"]) / 100)
            final_prices[each_product] = {
                "duration_price": duration_price,
                "trip_type_price": trip_type_price,
                "excess_duration_price": excess_duration_price,
                "excess_km_price":excess_km_price,
                "final_price": total_price,
                "discounted_price":discounted_price
            }
        return final_prices

    def check_valid_duration(self, product_ids, start_time, end_time):
        is_valid = True
        errors = defaultdict(list)

        duration_data = self.get_duration_data(product_ids)

        start_time_date_object = datetime.strptime(start_time, get_date_format())
        end_time_date_object = datetime.strptime(end_time, get_date_format())
        difference_date = (end_time_date_object - start_time_date_object)

        total_hours = ceil((difference_date.total_seconds() // 60) / 60)
        days = total_hours // 24
        hours = total_hours % 24
        for each_product_id in product_ids:
            each_duration_data = duration_data[each_product_id]
            if days == 0:
                min_time_duration = each_duration_data['min_hour_duration']
                max_time_duration = each_duration_data['max_hour_duration']
                if min_time_duration > hours:
                    is_valid = False
                    errors[each_product_id].append("Minimum time duration should be {} hours".format(min_time_duration))
                if max_time_duration < hours:
                    is_valid = False
                    errors[each_product_id].append("Maximum time duration should be {} hours".format(max_time_duration))

            else:
                min_time_duration = each_duration_data['min_day_duration']
                max_time_duration = each_duration_data['max_day_duration']

                if max_time_duration == days:
                    if hours != 0:
                        is_valid = False
                        errors[each_product_id].append("Maximum time duration should be {} days".format(max_time_duration))
                elif min_time_duration > days:
                    is_valid = False
                    errors[each_product_id].append("Minimum time duration should be {} days".format(min_time_duration))
                elif max_time_duration < days:
                    is_valid = False
                    errors[each_product_id].append("Maximum time duration should be {} days".format(max_time_duration))

        return is_valid, errors








