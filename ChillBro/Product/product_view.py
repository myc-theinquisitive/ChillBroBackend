from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from Product.BaseProduct.models import Product, ProductImage, ProductSize, ComboProductItems
from Product.BaseProduct.serializers import ProductSerializer, ProductImageSerializer, \
    ProductVerificationSerializer, ProductSizeSerializer
from Product.Hotel.views import HotelView
from Product.Rental.views import RentalView
from Product.Vehicle.views import VehicleView
from Product.HireAVehicle.views import HireAVehicleView
from Product.SelfRental.views import SelfRentalView
from Product.Driver.views import DriverView
from Product.TravelPackageVehicle.views import TravelPackageVehicleView
from Product.TravelAgency.views import TravelAgencyView
from Product.MakeYourOwnTrip.views import MakeYourOwnTripView
from Product.product_interface import ProductInterface
from Product.taggable_wrapper import key_value_content_type_model, key_value_tag_model
from typing import Dict
from django.conf import settings
from Product.wrapper import is_entity_id_valid, get_seller_id_wise_seller_details, \
    get_booked_count_of_product_id
from datetime import date, timedelta


class ProductView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.product_serializer = None
        self.product_specific_serializer = None

        self.product_specific_view = None
        self.product_specific_key = None
        self.product_specific_data = None

        self.product_object = None
        self.product_images = []

        self.key_value_content_type_model = key_value_content_type_model()
        self.key_value_tag_model = key_value_tag_model()

    @staticmethod
    def get_view_and_key_by_type(product_type):
        if product_type == "HOTEL":
            return HotelView(), "hotel_room"
        elif product_type == "RENTAL":
            return RentalView(), "rental_product"
        elif product_type == "DRIVER":
            return DriverView(), "driver"
        elif product_type == "VEHICLE":
            return VehicleView(), "vehicle"
        elif product_type == "HIRE_A_VEHICLE":
            return HireAVehicleView(), "hire_a_vehicle"
        elif product_type == "TRAVEL_PACKAGE_VEHICLE":
            return TravelPackageVehicleView(), "travel_package_vehicle"
        elif product_type == "TRAVEL_AGENCY":
            return TravelAgencyView(), "travel_agency"
        elif product_type == "MAKE_YOUR_OWN_TRIP":
            return MakeYourOwnTripView(), "make_your_own_trip"
        elif product_type == "SELF_RENTAL":
            return SelfRentalView(), "self_rental"
        return None, None

    # initialize the instance variables before accessing
    def initialize_product_class(self, product_data):

        product_object_defined = self.product_object is not None
        product_data_defined = product_data is not None

        # for update and get
        if product_object_defined:
            product_type = self.product_object.type
        # for create
        elif product_data_defined and "type" in product_data:
            product_type = product_data["type"]
            self.product_images = product_data.pop("images", [])
            if product_type == "MAKE_YOUR_OWN_TRIP":
                product_data['seller_id'] = settings.MYC_ID
        else:
            product_type = None

        self.product_specific_view, self.product_specific_key = self.get_view_and_key_by_type(product_type)

        if product_data:
            self.product_specific_data = product_data.pop(self.product_specific_key, None)
            self.product_specific_data['created_by'] = product_data['created_by']

        # for update
        if product_object_defined and product_data_defined:
            self.product_serializer = ProductSerializer(self.product_object, data=product_data)
            if self.product_specific_data:
                self.product_specific_data["product"] = self.product_object.id
        # for create
        elif product_data_defined:
            self.product_serializer = ProductSerializer(data=product_data)
        # for get
        elif product_object_defined:
            self.product_serializer = ProductSerializer(self.product_object)
        else:
            self.product_serializer = ProductSerializer()

    def validate_create_data(self, product_data: Dict) -> (bool, Dict):
        from .views import get_invalid_product_ids

        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(product_data)

        product_data_valid = self.product_serializer.is_valid()
        if not product_data_valid:
            is_valid = False
            errors.update(self.product_serializer.errors)

        # validate combo product items
        if "is_combo" in product_data and product_data["is_combo"]:
            if "combo_items" not in product_data or len(product_data["combo_items"]) < 2:
                is_valid = False
                errors["combo"].append("Combo Product must have atleast two products")
            else:
                product_ids = []
                for combo_product in product_data["combo_items"]:
                    product_ids.append(combo_product["product_id"])

                invalid_product_ids = get_invalid_product_ids(product_ids)
                if len(invalid_product_ids) != 0:
                    is_valid = False
                    errors["combo"].append("Some of the selected products are not valid")

        # validate product sizes
        if "has_sizes" in product_data and product_data["has_sizes"]:
            if "sizes" not in product_data or len(product_data["sizes"]) < 2:
                is_valid = False
                errors["sizes"].append("Must have atleast two product sizes")

            # size and order should be unique
            all_sizes = []
            all_order = []
            for product_size in product_data["sizes"]:
                all_sizes.append(product_size["size"])
                all_order.append(product_size["order"])
                if product_size["order"] <= 0:
                    is_valid = False
                    errors["sizes"].append("Order must be positive integer")

            if len(set(all_sizes)) != len(product_data["sizes"]):
                is_valid = False
                errors["sizes"].append("Sizes must be unique for product")
            if len(set(all_order)) != len(product_data["sizes"]):
                is_valid = False
                errors["sizes"].append("Order must be unique for product sizes")

        entity_id = product_data["seller_id"]
        is_entity_valid = is_entity_id_valid(entity_id)
        if not is_entity_valid:
            is_valid = False
            errors["entity_id"].append("Invalid Entity Id")

        # Validating images
        product_image_serializer = ProductImageSerializer(data=self.product_images, many=True)
        if not product_image_serializer.is_valid():
            is_valid = False
            errors["images"] = product_image_serializer.errors

        # Validating product specific data
        if not self.product_specific_view:
            is_valid = False
            errors["type"].append("Invalid Product Type")
        else:
            product_specific_data_valid, product_specific_errors = \
                self.product_specific_view.validate_create_data(self.product_specific_data)
            if not product_specific_data_valid:
                is_valid = False
                errors.update(product_specific_errors)

        return is_valid, errors

    def create(self, product_data: Dict) -> Dict:
        """
        product_data: {
            'name': string,
            'description': string,
            'type': string,
            'seller_id': string,
            'price': decimal,
            'discounted_price': decimal,
            'featured': boolean,
            'quantity_unlimited': boolean,
            'quantity': int,
            'is_combo': boolean,
            'combo_items': [
                {
                    'product_id': 'product_id',
                    'quantity': 1
                },
            ],
            'has_sizes': boolean,
            'sizes': ['size'],
            'tags': ['hotel', 'stay'],
            'images': [],
            'features': {
                'feature1': 'feature value',
                'feature2': 'feature 2 value'
            },
            'hotel_room': {
                'amenities': [
                    {
                        'amenity': string,
                        'is_available': boolean
                    }
                ]
            }
            'rental_product': {
            }
            'has_sub_products': boolean,
            'hire_a_vehicle': {
                "vehicle": string,
                "default_driver": string
            }
            'travel_package_vehicle': {
                "vehicle": string,
                "travel_package": string
            }
        }
        """

        base_product = self.product_serializer.create(product_data)
        self.product_specific_data["product"] = base_product.id

        # Product verification creation
        product_verification_data = {
            'product': base_product
        }
        product_verification_serializer = ProductVerificationSerializer()
        product_verification_serializer.create(product_verification_data)

        # Add Images to Product
        product_image_dicts = []
        for image_dict in self.product_images:
            product_image_dict = {
                "product": base_product.id,
                "image": image_dict["image"],
                "order": image_dict["order"]
            }
            product_image_dicts.append(product_image_dict)
        ProductImageSerializer.bulk_create(product_image_dicts)

        self.product_specific_view.create(self.product_specific_data)

        return {
            "id": base_product.id
        }

    def validate_update_data(self, product_data):
        from .views import get_invalid_product_ids

        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.product_object \
                = Product.objects.get(id=product_data["id"])
        except ObjectDoesNotExist:
            return False, {"errors": "Product does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(product_data)

        product_data_valid = self.product_serializer.is_valid()

        if not product_data_valid:
            is_valid = False
            errors.update(self.product_serializer.errors)

        # validate combo product items
        if "is_combo" in product_data and product_data["is_combo"]:
            if "add" in product_data["combo_items"]:
                product_ids = []
                for combo_product in product_data["combo_items"]["add"]:
                    product_ids.append(combo_product["product_id"])

                invalid_product_ids = get_invalid_product_ids(product_ids)
                if len(invalid_product_ids) != 0:
                    is_valid = False
                    errors["combo"].append("Some of the selected products are not valid")
            # No validations required for delete

        # validate product sizes
        if "has_sizes" in product_data and product_data["has_sizes"]:
            if "add" in product_data["sizes"]:
                product_sizes_serializer = ProductSizeSerializer(data=product_data["sizes"]["add"], many=True)
                product_sizes_valid = product_sizes_serializer.is_valid()
                if not product_sizes_valid:
                    is_valid = False
                    errors["sizes"].append(product_sizes_serializer.errors)
            # TODO: unique constraints are not handled in update case

        # Validating product specific data
        if not self.product_specific_view:
            is_valid = False
            errors["type"].append("Invalid Product Type")
        else:
            product_specific_data_valid, product_specific_errors = \
                self.product_specific_view.validate_update_data(self.product_specific_data)

            if not product_specific_data_valid:
                is_valid = False
                errors.update(product_specific_errors)

        return is_valid, errors

    def update(self, product_data: Dict) -> Dict:
        """
        product_data: {
            'slug': string,
            'name': string,
            'description': string,
            'type': string,
            'seller_id': string,
            'price': decimal,
            'discounted_price': decimal,
            'featured': boolean,
            'quantity_unlimited': boolean,
            'quantity': int,
            'is_combo': boolean,
            'combo_items': {
                'add': [
                    {
                        'product_id': 'product_id',
                        'quantity': 1
                    },
                ],
                'delete': ['product_id']
            },
            'has_sizes': boolean,
            'sizes': {
                'add': [
                    'size': 'XS',
                    'quantity': 10,
                ],
                'delete': ['XS', 'S']
            },
            'tags': ['hotel', 'stay', 'Single Room'],
            'features': {
                'add': {
                    'feature1': 'feature value 1',
                    'feature2': 'feature value 2',
                },
                'delete': {
                    'feature3': 'feature value 3'
                }
            },
            'hotel_room': {
                'hotel_room_id': string,
                'amenities': {
                    "add": [
                        {
                            "amenity": string,
                            "is_available": boolean
                        }
                    ]
                    "update": [
                        {
                            "id": string,
                            "amenity": string,
                            "is_available": boolean
                        }
                    ]
                    "delete": [
                        {
                            "id": string,
                            "amenity": string,
                            "is_available": boolean
                        }
                    ]
                }
            }
            'rental_product': {
            }
            'has_sub_products': boolean,
            'hire_a_vehicle': {
                "vehicle": string,
                "default_driver": string
            }
            'travel_package_vehicle': {
                "vehicle": string,
                "travel_package": string
            }
        }
        """

        self.product_serializer.update(self.product_object, product_data)
        self.product_specific_view.update(self.product_specific_data)

        return {
            "id": self.product_object.id
        }

    @staticmethod
    def update_product_response(response: Dict) -> Dict:
        response.pop("created_at", None)
        response.pop("updated_at", None)
        response.pop("active_from", None)
        response.pop("activation_status", None)
        response.pop("seller_id", None)
        response.pop("quantity", None)

        return response

    @staticmethod
    def get_product_id_wise_images(product_ids):
        product_images = ProductImage.objects.filter(product_id__in=product_ids)

        product_id_wise_images_dict = defaultdict(list)
        for product_image in product_images:
            image_url = product_image.image.url
            image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
            product_id_wise_images_dict[product_image.product_id].append(
                {
                    "id": product_image.id,
                    "image": image_url,
                    "order": product_image.order
                }
            )
        return product_id_wise_images_dict

    def get_product_id_wise_features(self, product_ids):
        ctype = self.key_value_content_type_model.objects.get_for_model(Product)
        product_features = self.key_value_tag_model.objects.filter(
            content_type=ctype, object_id__in=product_ids).all()

        product_id_wise_features_dict = defaultdict(list)
        for product_feature in product_features:
            product_id_wise_features_dict[product_feature.object_id].append(
                {
                    "feature": product_feature.key,
                    "value": product_feature.value
                }
            )
        return product_id_wise_features_dict

    @staticmethod
    def get_product_id_wise_sizes(product_ids):
        product_sizes = ProductSize.objects.filter(product_id__in=product_ids)

        product_id_wise_sizes_dict = defaultdict(list)
        for product_size in product_sizes:
            product_id_wise_sizes_dict[product_size.product_id].append(
                {
                    "size": product_size.size,
                    "is_available": True if product_size.quantity > 0 else False
                }
            )
        return product_id_wise_sizes_dict

    def get_product_id_wise_combo_product_details(self, product_ids):
        combo_product_items = ComboProductItems.objects.filter(product_id__in=product_ids)

        combo_item_ids = []
        product_id_wise_combo_quantity = defaultdict(int)
        for combo_product in combo_product_items:
            product_id = combo_product.combo_item.id
            combo_item_ids.append(product_id)
            product_id_wise_combo_quantity[product_id] = combo_product.quantity

        product_details = Product.objects.select_related("category").filter(id__in=combo_item_ids)
        product_id_wise_images_dict = self.get_product_id_wise_images(combo_item_ids)
        product_id_wise_sizes_dict = self.get_product_id_wise_sizes(combo_item_ids)

        product_id_wise_product_details = defaultdict(dict)
        for product in product_details:
            combo_product_details = ProductSerializer(product).data
            product_id_wise_product_details[product.id] = combo_product_details
            self.update_product_response(combo_product_details)

            combo_product_details["combo_quantity"] \
                = product_id_wise_combo_quantity[product.id]
            combo_product_details["category"] = {
                "id": product.category.id,
                "name": product.category.name
            }
            combo_product_details["images"] = product_id_wise_images_dict[product.id]
            combo_product_details["sizes"] = product_id_wise_sizes_dict[product.id]

        product_id_wise_combo_products_dict = defaultdict(list)
        for combo_item in combo_product_items:
            product_id_wise_combo_products_dict[combo_item.product.id].append(
                product_id_wise_product_details[combo_item.combo_item.id])

        return product_id_wise_combo_products_dict

    def get(self, product_id):
        self.product_object = Product.objects.select_related("category", "category_product").get(id=product_id)
        self.initialize_product_class(None)

        product_data = self.product_serializer.data
        product_data = self.update_product_response(product_data)

        product_id_wise_features_dict = self.get_product_id_wise_features([self.product_object.id])
        product_data["features"] = product_id_wise_features_dict[self.product_object.id]

        product_id_wise_images_dict = self.get_product_id_wise_images([self.product_object.id])
        product_data["images"] = product_id_wise_images_dict[self.product_object.id]

        seller_id_wise_seller_details = get_seller_id_wise_seller_details([self.product_object.seller_id])
        product_data["seller"] = seller_id_wise_seller_details[self.product_object.seller_id]

        product_id_wise_combo_products_dict = self.get_product_id_wise_combo_product_details([self.product_object.id])
        product_data["combo_items"] = product_id_wise_combo_products_dict[self.product_object.id]

        product_id_wise_sizes_dict = self.get_product_id_wise_sizes([self.product_object.id])
        product_data["sizes"] = product_id_wise_sizes_dict[self.product_object.id]

        product_data["category"] = {
            "id": self.product_object.category.id,
            "name": self.product_object.category.name
        }

        if self.product_object.category_product:
            product_data["category_product"] = {
                "id": self.product_object.category_product.id,
                "name": self.product_object.category_product.product_name
            }
        else:
            product_data["category_product"] = {
                "id": "",
                "name": ""
            }

        product_specific_data = self.product_specific_view.get(self.product_object.id)
        product_specific_data.pop("product", None)
        product_data[self.product_specific_key] = product_specific_data

        return product_data

    def get_by_ids(self, product_ids):
        from .views import add_average_rating_for_products

        products = Product.objects.select_related("category").filter(id__in=product_ids)
        product_id_wise_images_dict = self.get_product_id_wise_images(product_ids)
        product_id_wise_features_dict = self.get_product_id_wise_features(product_ids)
        product_id_wise_combo_products_dict = self.get_product_id_wise_combo_product_details(product_ids)
        product_id_wise_sizes_dict = self.get_product_id_wise_sizes(product_ids)

        seller_ids = []
        for product in products:
            seller_ids.append(product.seller_id)
        seller_id_wise_seller_details = get_seller_id_wise_seller_details(seller_ids)

        products_data = []
        group_products_by_type = defaultdict(list)
        for product in products:
            product_data = ProductSerializer(product).data
            product_data["features"] = product_id_wise_features_dict[product_data["id"]]
            product_data["images"] = product_id_wise_images_dict[product_data["id"]]
            product_data["combo_items"] = product_id_wise_combo_products_dict[product_data["id"]]
            product_data["sizes"] = product_id_wise_sizes_dict[product_data["id"]]
            product_data["seller"] = seller_id_wise_seller_details[product_data["seller_id"]]
            product_data["category"] = {
                "id": product.category.id,
                "name": product.category.name
            }
            product_data["category_product"] = {
                "id": product.category_product.id,
                "name": product.category_product.product_name
            }
            group_products_by_type[product_data["type"]].append(product_data)
            product_data = self.update_product_response(product_data)
            products_data.append(product_data)

        response = []
        for type in group_products_by_type:
            product_specific_view, product_key = self.get_view_and_key_by_type(type)

            product_specific_ids = []
            for product_dict in group_products_by_type[type]:
                product_specific_ids.append(product_dict["id"])

            product_specific_data = product_specific_view.get_by_ids(product_specific_ids)

            # combine product data with product specific data
            product_id_product_specific_data_dict = defaultdict(dict)
            for product_specific_dict in product_specific_data:
                product_id_product_specific_data_dict[product_specific_dict["product"]] = product_specific_dict
                product_specific_dict.pop("product", None)

            for product_dict in group_products_by_type[type]:
                product_dict[product_key] = product_id_product_specific_data_dict[product_dict["id"]]
                response.append(product_dict)

        add_average_rating_for_products(products_data)
        return products_data

    @staticmethod
    def get_product_id_wise_total_quantity_with_sizes(product_ids):
        products_size_quantity = ProductSize.objects.filter(product_id__in=product_ids).values('product_id') \
            .annotate(total_quantity=Sum('quantity')).values('product_id', 'total_quantity').order_by()

        product_id_wise_total_quantity_with_sizes = defaultdict(int)
        for product in products_size_quantity:
            product_id_wise_total_quantity_with_sizes[product["product_id"]] = product["total_quantity"]
        return product_id_wise_total_quantity_with_sizes

    def get_business_client_product_details(self, product_ids):
        from .views import calculate_product_net_price

        products = Product.objects.filter(id__in=product_ids)
        product_id_wise_images = self.get_product_id_wise_images(product_ids)
        product_id_wise_total_quantity_with_sizes = self.get_product_id_wise_total_quantity_with_sizes(product_ids)

        seller_ids = []
        for product in products:
            seller_ids.append(product.seller_id)
        seller_id_wise_seller_details = get_seller_id_wise_seller_details(seller_ids)

        today_date = date.today()
        tomorrow_date = today_date + timedelta(1)

        products_data = []
        for product in products:
            images = product_id_wise_images[product.id]
            sellers = seller_id_wise_seller_details[product.seller_id]

            total_booked = get_booked_count_of_product_id(product.id, today_date, tomorrow_date)
            discount = ((product.price - product.discounted_price) / product.price) * 100
            net_price_data = calculate_product_net_price(product.price, discount)

            total_quantity = product.quantity
            if product.has_sizes:
                total_quantity = product_id_wise_total_quantity_with_sizes[product.id]

            product_details = {
                'product_id': product.id,
                'name': product.name,
                'description': product.description,
                'images': images,
                'sellers': sellers,
                'bookings': {
                    'total': total_quantity,
                    'booked': total_booked,
                    'left': total_quantity - total_booked
                },
                'pricing': {
                    "actual_price": product.price,
                    "discount": discount,
                    "discounted_price": product.discounted_price,
                    "net_price": net_price_data["net_price"]
                }
            }
            products_data.append(product_details)
        return products_data

    def get_sub_products_ids(self, product_ids):
        products = Product.objects.filter(id__in=product_ids)

        group_products_by_type = defaultdict(list)
        for product in products:
            group_products_by_type[product.type].append(product.id)

        all_sub_products_ids = defaultdict()
        for type in group_products_by_type:
            product_specific_view, product_key = self.get_view_and_key_by_type(type)

            sub_products_ids_of_specific_type = product_specific_view.get_sub_products_ids(group_products_by_type[type])
            all_sub_products_ids.update(sub_products_ids_of_specific_type)

        return all_sub_products_ids

    def calculate_starting_prices(self, transport_ids_by_type, transport_ids_with_duration):
        all_products_prices = {}
        for type in transport_ids_with_duration:
            product_specific_view, product_key = self.get_view_and_key_by_type(type)

            product_price_data = product_specific_view.calculate_starting_prices(transport_ids_by_type[type], \
                                                                                transport_ids_with_duration[type] )
            all_products_prices.update(product_price_data)

        return all_products_prices

    def calculate_final_prices(self, products):
        product_ids = products.keys()
        all_products = Product.objects.filter(id__in=product_ids)

        group_products_by_type = defaultdict(dict)
        for product in all_products:
            group_products_by_type[product.type].update({product.id:products[product.id]})

        all_products_final_prices = defaultdict()
        for type in group_products_by_type:
            product_specific_view, product_key = self.get_view_and_key_by_type(type)

            products_final_prices = product_specific_view.calculate_final_prices(group_products_by_type[type])
            all_products_final_prices.update(products_final_prices)

        return all_products_final_prices

    # TODO: Add this to product interface
    def check_valid_duration(self, product_ids, start_time, end_time):
        products = Product.objects.filter(id__in=product_ids)

        group_products_by_type = defaultdict(list)
        for product in products:
            group_products_by_type[product.type].append(product.id)

        overall_is_valid = True
        overall_errors = defaultdict(list)
        for type in group_products_by_type:
            product_specific_view, product_key = self.get_view_and_key_by_type(type)

            is_valid, errors = product_specific_view.check_valid_duration(group_products_by_type[type], start_time, end_time)
            if not is_valid:
                overall_is_valid = is_valid
                overall_errors[type] = errors

        return overall_is_valid, overall_errors




