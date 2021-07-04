from ChillBro.helpers import get_date_format
from datetime import datetime
from math import ceil
from Product.product_interface import ProductInterface
from .serializers import SelfRentalSerializer, SelfRentalDistancePriceSerializer, SelfRentalDurationDetailsSerializer
from typing import Dict
from .models import SelfRental, SelfRentalDistancePrice, SelfRentalDurationDetails
from .wrapper import get_vehicle_data_by_id, get_vehicle_id_wise_details, check_vehicle_exists_by_id
from collections import defaultdict


def check_distance_price_self_rental_by_id(distance_price_ids, self_rental_id):
    from .models import SelfRentalDistancePrice
    distance_price_objects = SelfRentalDistancePrice.objects.filter(id__in=distance_price_ids,
                                                          self_rental_id=self_rental_id).values_list('id')
    if len(list(distance_price_objects)) != len(distance_price_ids):
        invalid_ids = set(distance_price_ids) - set(distance_price_objects)
        return False, list(invalid_ids)
    return True, []


def get_distance_price_data(self_rental_ids):
    distance_price = SelfRentalDistancePrice.objects.filter(self_rental_id__in=self_rental_ids)

    distance_price_serializer = SelfRentalDistancePriceSerializer(distance_price, many=True)
    return distance_price_serializer.data


class SelfRentalView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.self_rental_serializer = None
        self.self_rental_object = None
        self.distance_price_data = None
        self.duration_details = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, self_rental_data):
        if self_rental_data:
            self.distance_price_data = self_rental_data.pop("distance_price", [])
            self.duration_details = self_rental_data.pop("duration_details", [])

        self_rental_object_defined = self.self_rental_object is not None
        self_rental_data_defined = self_rental_data is not None

        # for update
        if self_rental_object_defined and self_rental_data_defined:
            self.self_rental_serializer = SelfRentalSerializer(
                self.self_rental_object, data=self_rental_data)
        # for create
        elif self_rental_data_defined:
            self.self_rental_serializer = SelfRentalSerializer(data=self_rental_data)
        # for get
        elif self_rental_object_defined:
            self.self_rental_serializer = SelfRentalSerializer(self.self_rental_object)
        else:
            self.self_rental_serializer = SelfRentalSerializer()

    def validate_create_data(self, self_rental_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        vehicle_data = check_vehicle_exists_by_id(self_rental_data['vehicle'])
        if not vehicle_data:
            is_valid = False
            errors['vehicle'] = "Vehicle does not exist"
            return is_valid, errors

        if vehicle_data.registration_type != "RENTAL":
            is_valid = False
            errors['registration_type'] = "Only Commercial Vehicle allowed"

        km_limit_list = list(map(lambda x: x['km_limit'], self.distance_price_data))
        if len(set(km_limit_list)) != len(km_limit_list):
            is_valid = False
            errors['km_limit'] = "KM limit values must be unique"

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        distance_price_serializer = SelfRentalDistancePriceSerializer(
            data=self.distance_price_data, many=True)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors["distance_price"].append(distance_price_serializer.errors)

        duration_details_serializer = SelfRentalDurationDetailsSerializer(data=self.duration_details)
        if not duration_details_serializer.is_valid():
            is_valid = False
            errors["duration_details"].append(duration_details_serializer.errors)

        return is_valid, errors

    def create(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated,
            "excess_price_per_hour": int,
            "vehicle_id": string
            distance_price: [
                    {
                        'price': int,
                        'km_limit': int,
                        'excess_km_price':int,
                        'excess_price_per_hour': int,
                        is_infinity: Boolean
                    }
                ],
            "duration_details":{
                'min_hour_duration': int,
                'max_hour_duration': int,
                'min_day_duration': int,
                'max_day:duration': int,
            }
        }
        """

        self_rental_object = self.self_rental_serializer.create(self_rental_data)

        for distance_price in self.distance_price_data:
            distance_price["self_rental"] = self_rental_object
            if 'is_infinity' in distance_price:
                distance_price['excess_km_price'] = 0 if distance_price['is_infinity'] else distance_price['excess_km_price']
            else:
                distance_price['is_infinity'] = False

        distance_price_serializer = SelfRentalDistancePriceSerializer()
        distance_price_serializer.bulk_create(self.distance_price_data)

        self.duration_details["self_rental"] = self_rental_object
        duration_details_serializer = SelfRentalDurationDetailsSerializer()
        duration_details_serializer.create(self.duration_details)

        return {
            "id": self_rental_object.id
        }

    def validate_update_data(self, self_rental_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.self_rental_object \
                = SelfRental.objects.get(product_id=self_rental_data["product"])
        except SelfRental.DoesNotExist:
            return False, {"errors": "Self Rental does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(self_rental_data)

        km_limit_list = list(map(lambda x: x['km_limit'], self.distance_price_data['add']))

        if len(set(km_limit_list)) != len(km_limit_list):
            is_valid = False
            errors['km_limit'] = "KM limit values must be unique"
            return is_valid, errors

        km_limit_errors = SelfRentalDistancePrice.objects.filter(self_rental_id=self.self_rental_object['id'],
                                                       km_limit__in=km_limit_list).values_list('km_limit')

        if len(km_limit_errors) > 0:
            is_valid = False
            errors['km_limit already exists'] = km_limit_errors

        distance_price_ids = list(
            map(lambda x: x['id'], self.distance_price_data['change'] + self.distance_price_data['delete']))
        invalid_distance_price_ids = check_distance_price_self_rental_by_id(distance_price_ids,
                                                                            self.self_rental_object['id'])
        if invalid_distance_price_ids[0]:
            is_valid = False
            errors["invalid distance_price id's"] = invalid_distance_price_ids[1]

        self_rental_data_valid = self.self_rental_serializer.is_valid()
        if not self_rental_data_valid:
            is_valid = False
            errors.update(self.self_rental_serializer.errors)

        distance_price_serializer = SelfRentalDistancePriceSerializer(data=self.distance_price_data)
        if not distance_price_serializer.is_valid():
            is_valid = False
            errors.update(distance_price_serializer.errors)
            return is_valid, errors

        duration_details_serializer = SelfRentalDurationDetailsSerializer(data=self.duration_details)
        if not duration_details_serializer.is_valid():
            is_valid = False
            errors["duration_details"].append(duration_details_serializer.errors)

        return is_valid, errors

    def update(self, self_rental_data):
        """
        self_rental: {
            "product_id": string, # internal data need not be validated
            "vehicle": string,
            "distance_price" :{
                "add": [
                    {
                        'price': int,
                        'km_limit': int,
                        'excess_km_price': int,
                        'excess_price_per_hour': int,
                    }
                ],
                "change": [
                    {
                        'id': string,
                        'price': int,
                        'km_limit': int,
                        'excess_km_price': int,
                        'excess_price_per_hour': int,
                   }
                ]
                "delete": [
                    {
                        'id': string
                    }
                ]
            },
            "duration_details":{
                'min_hour_duration': int,
                'max_hour_duration': int,
                'min_day_duration': int,
                'max_day:duration': int,
            }
        }
        """

        self.self_rental_serializer.update(self.self_rental_object, self_rental_data)
        distance_price_serializer = SelfRentalDistancePriceSerializer()
        distance_price_serializer.bulk_create(self.distance_price_data["add"])
        distance_price_serializer.bulk_update(self.distance_price_data["change"])
        distance_price_serializer.bulk_delete(self.distance_price_data["delete"])
        duration_details_serializer= SelfRentalDurationDetails.objects.filter(hire_a_vehicle=self.hire_a_vehicle_object)
        duration_details_serializer.update(self.duration_details)

    def get(self, product_id):
        self.self_rental_object = SelfRental.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        self_rental_data = self.self_rental_serializer.data
        vehicle_data = get_vehicle_data_by_id(self_rental_data["vehicle"])
        self_rental_data["distance_price"] = self.get_price_data([self.self_rental_object])[product_id]
        self_rental_data["duration_details"] = self.get_duration_data([self.self_rental_object])[product_id]
        self_rental_data["vehicle"] = vehicle_data

        return self_rental_data

    def get_by_ids(self, product_ids):
        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)

        self_rental_serializer = SelfRentalSerializer(self_rentals, many=True)
        self_rentals_data = self_rental_serializer.data

        self_rental_id_wise_distance_prices = self.get_price_data(self_rentals)
        self_rental_id_wise_duration_details = self.get_duration_data(self_rentals)

        vehicle_ids = []
        for self_rental_data in self_rentals_data:
            vehicle_ids.append(self_rental_data["vehicle"])

        vehicle_id_wise_details = get_vehicle_id_wise_details(vehicle_ids)
        for self_rental_data in self_rentals_data:
            self_rental_data["vehicle"] = vehicle_id_wise_details[self_rental_data["vehicle"]]
            self_rental_data['distance_price'] = self_rental_id_wise_distance_prices[self_rental_data['product']]
            self_rental_data['duration_details'] = self_rental_id_wise_duration_details[self_rental_data['product']]

        return self_rentals_data

    def get_sub_products_ids(self, product_ids):
        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)
        self_rentals_sub_products_ids = defaultdict()

        for each_self_rental in self_rentals:
            self_rentals_sub_products_ids[each_self_rental.product_id] = \
                {
                    each_self_rental.vehicle_id:
                    {
                        "quantity": 1,
                        "size":{}
                    }
                }

        return self_rentals_sub_products_ids

    @staticmethod
    def get_price_data(self_rentals):
        self_rentals_data = defaultdict(dict)
        self_rentals_price_details = defaultdict(dict)
        self_rentals_ids = []

        for each_self_rental in self_rentals:
            self_rentals_ids.append(each_self_rental.id)

        self_rental_distance_price_data = SelfRentalDistancePrice.objects \
            .filter(self_rental__in=self_rentals_ids)
        self_rental_distance_price_serializer = \
            SelfRentalDistancePriceSerializer(self_rental_distance_price_data, many=True)

        for each_distance_price in self_rental_distance_price_serializer.data:
            self_rentals_data[each_distance_price["self_rental"]][each_distance_price['km_limit']] = each_distance_price

        for each_self_rental in self_rentals:
            self_rentals_price_details[each_self_rental.product_id].update(self_rentals_data[each_self_rental.id])

        return self_rentals_price_details

    @staticmethod
    def get_duration_data(self_rentals):
        self_rentals_data = defaultdict()
        self_rentals_duration_details = defaultdict()
        self_rentals_ids = []

        for each_self_rental in self_rentals:
            self_rentals_ids.append(each_self_rental.id)

        self_rental_duration_details_data = SelfRentalDurationDetails.objects \
            .filter(self_rental__in=self_rentals_ids)
        self_rental_duration_details_serializer = \
            SelfRentalDurationDetailsSerializer(self_rental_duration_details_data, many=True)

        for each_duration_details in self_rental_duration_details_serializer.data:
            self_rentals_data[each_duration_details["self_rental"]] = each_duration_details

        for each_self_rental in self_rentals:
            self_rentals_duration_details[each_self_rental.product_id] = \
                self_rentals_data[each_self_rental.id]

        return self_rentals_duration_details

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)
        self_rentals_price_details = self.get_price_data(self_rentals)
        result = defaultdict()

        for each_self_rental in self_rentals:
            each_self_rental_details = product_details_with_ids[each_self_rental.product_id]
            start_time_date_object = each_self_rental_details['start_time']
            end_time_date_object = each_self_rental_details['end_time']
            quantity = each_self_rental_details["quantity"]
            discount_percentage = each_self_rental_details["discount_percentage"]
            km_limit_choosen = each_self_rental_details["km_limit_choosen"]

            difference_date = (end_time_date_object - start_time_date_object)
            total_hours = ceil((difference_date.total_seconds() // 60) / 60)
            days = ceil(total_hours / 24)

            price_data = self_rentals_price_details[each_self_rental.product_id][km_limit_choosen]

            duration_price = float(price_data["price"]) * days
            total_price = duration_price * quantity
            discounted_price = total_price - ((total_price * float(discount_percentage)) / 100)

            result[each_self_rental.product_id] = {
                "duration_price": duration_price,
                "total_price": total_price,
                "discounted_price": discounted_price
            }

        return result

    def calculate_final_prices(self, products):
        final_prices = defaultdict()
        for each_product in products:
            transport_details = products[each_product]["transport_details"]
            print(transport_details,"transport_details")

            start_time = datetime.strptime(products[each_product]["start_time"], get_date_format())
            booking_end_time = datetime.strptime(products[each_product]["booking_end_time"], get_date_format())
            present_end_time = datetime.strptime(products[each_product]["present_end_time"], get_date_format())

            booking_difference_date = (booking_end_time - start_time)
            booking_total_hours = ceil((booking_difference_date.total_seconds() // 60) / 60)
            days = booking_total_hours // 24
            hours = booking_total_hours % 24
            duration_price = float(transport_details["distance_details"]["price"]) * (days + hours/24)

            if present_end_time > booking_end_time:
                excess_difference_date = (present_end_time - booking_end_time)
                excess_total_hours = ceil((excess_difference_date.total_seconds() // 60) / 60)
                excess_days = excess_total_hours // 24
                excess_hours = excess_total_hours % 24
                excess_duration_price = float(transport_details["distance_details"]["price"]) *\
                                        (excess_days + excess_hours/24)
            else:
                excess_duration_price = 0

            max_km_can_travel = transport_details["distance_details"]["km_limit"] * days +\
                                transport_details["distance_details"]["km_limit"] * hours //24
            km_travelled = transport_details["ending_km_value"] - transport_details["starting_km_value"]
            if km_travelled > max_km_can_travel:
                excess_km_travelled = km_travelled - max_km_can_travel
                excess_km_price = float(transport_details["distance_details"]["excess_km_price"]) *\
                                  excess_km_travelled
            else:
                excess_km_price = 0

            total_price = (excess_km_price + excess_duration_price) * products[each_product]["quantity"]
            discounted_price = total_price - ((total_price * float(products[each_product]["discount_percentage"]))/ 100)
            final_prices[each_product] = {
                "duration_price": duration_price,
                "trip_type_price": 0,
                "excess_duration_price": excess_duration_price,
                "excess_km_price": excess_km_price,
                "final_price": total_price,
                "discounted_price": discounted_price
            }

        return final_prices

    def check_valid_duration(self, product_ids, start_time, end_time):
        is_valid = True
        errors = defaultdict(list)

        self_rentals = SelfRental.objects.filter(product_id__in=product_ids)
        duration_data = self.get_duration_data(self_rentals)

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

