from collections import defaultdict
from datetime import datetime
from math import ceil

from djangochannelsrestframework import generics

from Bookings.helpers import get_date_format
from .models import RentalProduct
from .serializers import RentalProductSerializer
from ..product_interface import ProductInterface
from typing import Dict
from Product.BaseProduct.models import Product
from ChillBro.constants import PriceTypes

class RentalView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.rental_serializer = None
        self.rental_object = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, rental_data):

        rental_object_defined = self.rental_object is not None
        rental_data_defined = rental_data is not None

        # for update
        if rental_object_defined and rental_data_defined:
            self.rental_serializer = RentalProductSerializer(self.rental_object, data=rental_data)
        # for create
        elif rental_data_defined:
            self.rental_serializer = RentalProductSerializer(data=rental_data)
        # for get
        elif rental_object_defined:
            self.rental_serializer = RentalProductSerializer(self.rental_object)
        else:
            self.rental_serializer = RentalProductSerializer()

    def validate_create_data(self, rental_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(rental_data)

        rental_data_valid = self.rental_serializer.is_valid()
        if not rental_data_valid:
            is_valid = False
            errors.update(self.rental_serializer.errors)

        return is_valid, errors

    def create(self, rental_data):
        """
        rental_product: {
            "product_id": string, # internal data need not be validated
        }
        """

        rental_object = self.rental_serializer.create(rental_data)

        return {
            "id": rental_object.id
        }

    def validate_update_data(self, rental_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.rental_object \
                = RentalProduct.objects.get(product_id=rental_data["product"])
        except RentalProduct.DoesNotExist:
            return False, {"errors": "Rental Product does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(rental_data)

        rental_data_valid = self.rental_serializer.is_valid()
        if not rental_data_valid:
            is_valid = False
            errors.update(self.rental_serializer.errors)

        return is_valid, errors

    def update(self, rental_data):
        """
        rental_product: {
        }
        """

        self.rental_serializer.update(self.rental_object, rental_data)

    @staticmethod
    def update_rental_response(response: Dict) -> Dict:
        # Other than product id make necessary modification
        # Will remove product id in product view as it is required there
        # response.pop("product", None)
        return response

    def get(self, product_id):
        self.rental_object = RentalProduct.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        rental_data = self.rental_serializer.data
        rental_data = self.update_rental_response(rental_data)

        return rental_data

    def get_by_ids(self, product_ids):
        rental_products = RentalProduct.objects.filter(product_id__in=product_ids)

        rental_serializer = RentalProductSerializer(rental_products, many=True)
        rentals_data = rental_serializer.data

        for rental_data in rentals_data:
            rental_data = self.update_rental_response(rental_data)

        return rentals_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_details_with_ids):
        products = Product.objects.filter(id__in=product_ids)
        starting_prices = defaultdict()
        for each_product in products:
            each_rental_details = product_details_with_ids[each_product.product_id]
            start_time_date_object = each_rental_details['start_time']
            end_time_date_object = each_rental_details['end_time']
            quantity = each_rental_details["quantity"]
            discount_percentage = each_rental_details["discount_percentage"]

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

