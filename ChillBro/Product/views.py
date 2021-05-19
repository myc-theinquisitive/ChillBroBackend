from django.db.models import Subquery, OuterRef, PositiveIntegerField
from .BaseProduct.serializers import ProductVerificationSerializer, ProductVerificationUpdateInputSerializer
from .Category.views import *
from .BaseProduct.views import *
from .Hotel.views import *
from .Rental.views import RentalView
from .Seller.views import *
from .product_interface import ProductInterface
from .serializers import ProductSerializer, IdsListSerializer, SellerProductSerializer, NetPriceSerializer, \
    GetProductsBySearchFilters, GetBusinessClientProductsByStatusSerializer
from .Hotel.views import HotelView
from collections import defaultdict
from .taggable_wrapper import key_value_content_type_model, key_value_tag_model
from .wrapper import is_entity_id_valid, get_booked_count_of_product_id, get_seller_id_wise_seller_details, \
    filter_seller_ids_by_city, average_rating_query_for_product, get_product_id_wise_average_rating
from .models import SellerProduct
from rest_framework import status
from .constants import COMMISION_FEE_PERCENT, TRANSACTION_FEE_PERCENT, GST_PERCENT, FIXED_FEE_PERCENT
from .BaseProduct.models import Product, ProductVerification, ComboProductItems, ProductSize
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsOwnerById, IsUserOwner, IsSellerProduct, \
    IsBusinessClientEntities, IsEmployeeEntities
from .BaseProduct.constants import ActivationStatus
from datetime import date, timedelta, datetime
from .helpers import get_date_format
from decimal import Decimal


def get_invalid_product_ids(product_ids):
    existing_product_ids = Product.objects.filter(id__in=product_ids).values_list("id", flat=True)
    return set(product_ids) - set(existing_product_ids)


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
        else:
            product_type = None

        self.product_specific_view, self.product_specific_key = self.get_view_and_key_by_type(product_type)
        if product_data:
            self.product_specific_data = product_data.pop(self.product_specific_key, None)

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
                product_ids = product_data["combo_items"]
                invalid_product_ids = get_invalid_product_ids(product_ids)
                if len(invalid_product_ids) != 0:
                    is_valid = False
                    errors["combo"].append("Some of the selected products are not valid")

        # validate product sizes
        if "has_sizes" in product_data and product_data["has_sizes"]:
            if "sizes" not in product_data or len(product_data["sizes"]) < 2:
                is_valid = False
                errors["sizes"].append("Must have atleast two product sizes")

        # Entity details validation
        if "entity_id" not in product_data:
            is_valid = False
            errors["entity_id"].append("This field is required")
        else:
            entity_id = product_data["entity_id"]
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
            'price': decimal,
            'discounted_price': decimal,
            'featured': boolean,
            'is_combo': boolean,
            'combo_items': ['product_id']
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
        }
        """

        base_product = self.product_serializer.create(product_data)
        self.product_specific_data["product"] = base_product.id

        # Link seller to product
        seller_product_data = {
            "product_id": base_product.id,
            "seller_id": product_data["entity_id"]
        }
        seller_product_serializer = SellerProductSerializer()
        seller_product_serializer.create(seller_product_data)

        # Product verification creation
        product_verification_data = {
            'product': base_product
        }
        product_verification_serializer = ProductVerificationSerializer()
        product_verification_serializer.create(product_verification_data)

        # Add Images to Product
        product_image_dicts = []
        for image in self.product_images:
            product_image_dict = {
                "product": base_product.id,
                "image": image
            }
            product_image_dicts.append(product_image_dict)
        ProductImageSerializer.bulk_create(product_image_dicts)

        self.product_specific_view.create(self.product_specific_data)

        return {
            "id": base_product.id
        }

    def validate_update_data(self, product_data):
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
                product_ids = product_data["combo_items"]["add"]
                invalid_product_ids = get_invalid_product_ids(product_ids)
                if len(invalid_product_ids) != 0:
                    is_valid = False
                    errors["combo"].append("Some of the selected products are not valid")
            # No validations required for delete
        # No validation product sizes

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
            'price': decimal,
            'discounted_price': decimal,
            'featured': boolean,
            'is_combo': boolean,
            'combo_items': {
                'add': ['product_id'],
                'delete': ['product_id']
            }
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
        response.pop("slug", None)

        return response

    @staticmethod
    def get_product_id_wise_images(product_ids):
        product_images = ProductImage.objects.filter(product_id__in=product_ids)

        product_id_wise_images_dict = defaultdict(list)
        for product_image in product_images:
            image_url = product_image.image.url
            image_url = image_url.replace(settings.IMAGE_REPLACED_STRING,"")
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
    def get_product_id_wise_sellers(product_ids):
        product_sellers = SellerProduct.objects.filter(product_id__in=product_ids)

        seller_ids = []
        for product_seller in product_sellers:
            seller_ids.append(product_seller.seller_id)
        seller_id_wise_seller_names = get_seller_id_wise_seller_details(seller_ids)

        product_id_wise_sellers_dict = defaultdict(list)
        for product_seller in product_sellers:
            seller_id = product_seller.seller_id
            product_id_wise_sellers_dict[product_seller.product_id].append(
                {
                    "seller_id": seller_id,
                    "outlet_name": seller_id_wise_seller_names[seller_id]['name']
                }
            )
        return product_id_wise_sellers_dict

    @staticmethod
    def get_product_id_wise_sizes(product_ids):
        product_sizes = ProductSize.objects.filter(product_id__in=product_ids)

        product_id_wise_sizes_dict = defaultdict(list)
        for product_size in product_sizes:
            product_id_wise_sizes_dict[product_size.product_id].append(product_size.size)
        return product_id_wise_sizes_dict

    def get_product_id_wise_combo_product_details(self, product_ids):
        combo_product_items = ComboProductItems.objects.filter(product_id__in=product_ids)
        combo_item_ids = []
        for combo_product in combo_product_items:
            combo_item_ids.append(combo_product.combo_item.id)

        product_details = Product.objects.filter(id__in=combo_item_ids)
        product_id_wise_product_details = defaultdict(dict)
        for product in product_details:
            product_id_wise_product_details[product.id] = ProductSerializer(product).data
            self.update_product_response(product_id_wise_product_details[product.id])

        product_id_wise_combo_products_dict = defaultdict(list)
        for combo_item in combo_product_items:
            product_id_wise_combo_products_dict[combo_item.product.id].append(
                product_id_wise_product_details[combo_item.combo_item.id])

        return product_id_wise_combo_products_dict

    def get(self, product_id):
        self.product_object = Product.objects.select_related("category").get(id=product_id)
        self.initialize_product_class(None)

        product_data = self.product_serializer.data
        product_data = self.update_product_response(product_data)

        product_id_wise_features_dict = self.get_product_id_wise_features([self.product_object.id])
        product_data["features"] = product_id_wise_features_dict[self.product_object.id]

        product_id_wise_images_dict = self.get_product_id_wise_images([self.product_object.id])
        product_data["images"] = product_id_wise_images_dict[self.product_object.id]

        product_id_wise_sellers_dict = self.get_product_id_wise_sellers([self.product_object.id])
        product_data["sellers"] = product_id_wise_sellers_dict[self.product_object.id]

        product_id_wise_combo_products_dict = self.get_product_id_wise_combo_product_details([self.product_object.id])
        product_data["combo_items"] = product_id_wise_combo_products_dict[self.product_object.id]

        product_id_wise_sizes_dict = self.get_product_id_wise_sizes([self.product_object.id])
        product_data["sizes"] = product_id_wise_sizes_dict[self.product_object.id]

        product_data["category"] = {
            "id": self.product_object.category.id,
            "name": self.product_object.category.name
        }

        product_specific_data = self.product_specific_view.get(self.product_object.id)
        product_specific_data.pop("product", None)
        product_data[self.product_specific_key] = product_specific_data

        return product_data

    def get_by_ids(self, product_ids):

        products = Product.objects.select_related("category").filter(id__in=product_ids)

        product_id_wise_images_dict = self.get_product_id_wise_images(product_ids)
        product_id_wise_features_dict = self.get_product_id_wise_features(product_ids)
        product_id_wise_sellers_dict = self.get_product_id_wise_sellers(product_ids)
        product_id_wise_combo_products_dict = self.get_product_id_wise_combo_product_details(product_ids)
        product_id_wise_sizes_dict = self.get_product_id_wise_sizes(product_ids)

        products_data = []
        group_products_by_type = defaultdict(list)
        for product in products:
            product_data = ProductSerializer(product).data
            product_data = self.update_product_response(product_data)
            product_data["features"] = product_id_wise_features_dict[product_data["id"]]
            product_data["images"] = product_id_wise_images_dict[product_data["id"]]
            product_data["sellers"] = product_id_wise_sellers_dict[product_data["id"]]
            product_data["combo_items"] = product_id_wise_combo_products_dict[product_data["id"]]
            product_data["sizes"] = product_id_wise_sizes_dict[product_data["id"]]
            product_data["category"] = {
                "id": product.category.id,
                "name": product.category.name
            }
            group_products_by_type[product_data["type"]].append(product_data)
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

        return products_data

    def get_business_client_product_details(self, product_ids):
        products = Product.objects.filter(id__in=product_ids)
        product_id_wise_images = self.get_product_id_wise_images(product_ids)
        product_id_wise_sellers_dict = self.get_product_id_wise_sellers(product_ids)

        today_date = date.today()
        tomorrow_date = today_date + timedelta(1)

        products_data = []
        for product in products:
            images = product_id_wise_images[product.id]
            sellers = product_id_wise_sellers_dict[product.id]

            total_booked = get_booked_count_of_product_id(product.id, today_date, tomorrow_date)
            discount = ((product.price - product.discounted_price) / product.price) * 100
            net_price_data = calculate_product_net_price(product.price, discount)

            product_details = {
                'product_id': product.id,
                'name': product.name,
                'description': product.description,
                'images': images,
                'sellers': sellers,
                'bookings': {
                    # TODO: if product has sizes then product quantity will be sum of all sizes of product
                    'total': product.quantity,
                    'booked': total_booked,
                    'left': product.quantity - total_booked
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


def calculate_product_net_price(selling_price, discount):
    final_selling_price = selling_price - (selling_price * discount) / 100
    commission_fee = final_selling_price * COMMISION_FEE_PERCENT / 100
    transaction_fee = final_selling_price * TRANSACTION_FEE_PERCENT / 100
    fixed_fee = final_selling_price * FIXED_FEE_PERCENT / 100
    gst = final_selling_price * GST_PERCENT / 100
    net_price = final_selling_price - (commission_fee + transaction_fee + fixed_fee + gst)

    return {
        "net_price": net_price,
        "details": {
            "final_selling_price": final_selling_price,
            "commission_fee": commission_fee,
            "transaction_fee": transaction_fee,
            "fixed_fee": fixed_fee,
            "gst": gst
        }
    }


def add_verification_details_to_product(products_list):
    product_ids = []
    for product in products_list:
        product_ids.append(product["id"])

    product_verifications = ProductVerification.objects.filter(product_id__in=product_ids)
    product_verification_per_product_id_dict = {}
    for product_verification in product_verifications:
        product_verification_per_product_id_dict[product_verification.product_id] = product_verification

    for product in products_list:
        product_verification = product_verification_per_product_id_dict[product["id"]]

        employee_name = None
        employee_email = None
        if product_verification.verified_by:
            employee_name = product_verification.verified_by.first_name
            employee_email = product_verification.verified_by.email
        product["verification"] = {
            "comments": product_verification.comments,
            "verified_by": {
                'name': employee_name,
                'email': employee_email
            },
            "updated_at": product_verification.updated_at.strftime(get_date_format())
        }


class BusinessClientProductDetails(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        product_id = kwargs['product_id']
        products_data = ProductView().get_business_client_product_details([product_id])

        if len(products_data) != 1:
            return Response({"message": "invalid product id"}, 400)

        return Response(products_data[0], 200)


class ProductList(APIView):
    permission_classes = (IsAuthenticated,)
    product_view = ProductView()

    def post(self, request):
        is_valid, errors = self.product_view.validate_create_data(request.data)
        if not is_valid:
            return Response(errors, 400)

        response_data = self.product_view.create(request.data)
        return Response(data=response_data, status=201)

    def get(self, request, format=None):
        serializer = IdsListSerializer(data=request.data)
        if serializer.is_valid():
            response_data = self.product_view.get_by_ids(serializer.data["ids"])
            return Response({"results": response_data}, 200)
        else:
            return Response({"errors": serializer.errors}, 400)


class ProductDetail(APIView):
    permission_classes = (IsAuthenticated,)
    product_view = ProductView()

    def put(self, request, id):
        request.data["id"] = id

        is_valid, errors = self.product_view.validate_update_data(request.data)
        if not is_valid:
            return Response(errors, 400)

        response_data = self.product_view.update(request.data)
        return Response(data=response_data, status=201)

    def get(self, request, id, format=None, *args):
        try:
            response_data = self.product_view.get(id)
        except ObjectDoesNotExist:
            return Response({"errors": "Product does not Exist!!!"}, 400)

        return Response(data=response_data, status=200)

    def delete(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"errors": "Product does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)
        product.status = ActivationStatus.DELETED.value
        product.save()
        return Response({"success": "Deleted Successfully"}, status=status.HTTP_200_OK)


class GetProductsByCategory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    product_view = ProductView()

    @staticmethod
    def apply_filters(category, filter_data):
        # applying category filter
        filter_products = Product.objects.filter(category_id=category.id)

        # applying search filter
        if filter_data["search_text"]:
            filter_products = filter_products.search(filter_data["search_text"])

        # applying price filters
        price_filter = filter_data["price_filter"]
        if price_filter["applied"]:
            filter_products = filter_products.filter(
                discounted_price__gte=price_filter["min_amount"], discounted_price__lte=price_filter["max_amount"])

        # applying location Filters
        location_filter = filter_data["location_filter"]
        if location_filter["applied"]:
            product_ids = filter_products.values_list("id", flat=True)
            seller_ids = SellerProduct.objects.filter(product_id__in=product_ids)\
                .values_list("seller_id", flat=True)
            city_seller_ids = filter_seller_ids_by_city(seller_ids, location_filter["city"])
            city_product_ids = SellerProduct.objects.filter(
                seller_id__in=city_seller_ids, product_id__in=product_ids).values_list("product_id", flat=True)
            filter_products = filter_products.filter(id__in=city_product_ids)

        return filter_products.values_list("id", flat=True)

    @staticmethod
    def apply_sort_filter(query_set, sort_filter):
        if sort_filter == "PRICE_LOW_TO_HIGH":
            return query_set.order_by('discounted_price')
        elif sort_filter == "PRICE_HIGH_TO_LOW":
            return query_set.order_by('-discounted_price')
        elif sort_filter == "AVERAGE_RATING":
            ratings_query = average_rating_query_for_product(OuterRef('id'))
            return query_set.annotate(
                average_rating=Subquery(
                    queryset=ratings_query,
                    output_field=PositiveIntegerField()
                )
            ).order_by('-average_rating')
        return query_set

    @staticmethod
    def sort_results(products_response, sort_filter):
        if sort_filter == "PRICE_LOW_TO_HIGH":
            products_response.sort(key=lambda product_response: Decimal(product_response['discounted_price']))
        elif sort_filter == "PRICE_HIGH_TO_LOW":
            products_response.sort(
                key=lambda product_response: Decimal(product_response['discounted_price']), reverse=True)
        elif sort_filter == "AVERAGE_RATING":
            products_response.sort(
                key=lambda product_response: Decimal(product_response['rating']), reverse=True)

    @staticmethod
    def add_average_rating_for_products(products_response):
        product_ids = []
        for product in products_response:
            product_ids.append(product["id"])

        product_id_wise_rating = get_product_id_wise_average_rating(product_ids)
        for product in products_response:
            product["rating"] = product_id_wise_rating[product["id"]]

    def get(self, request, *args, **kwargs):

        input_serializer = GetProductsBySearchFilters(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get products", "errors": input_serializer.errors}, 400)

        try:
            # TODO: Modify to get products for intermediate levels that are not linked to product
            category = Category.objects.get(name__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Category!!!"}, 400)

        sort_filter = request.data["sort_filter"]
        product_ids = self.apply_filters(category, request.data)
        self.queryset = Product.objects.filter(id__in=product_ids)
        self.queryset = self.apply_sort_filter(self.queryset, sort_filter)

        response = super().get(request, args, kwargs)
        response_data = response.data

        product_ids = []
        for product in response_data["results"]:
            product_ids.append(product["id"])
        response_data["results"] = self.product_view.get_by_ids(product_ids)
        self.add_average_rating_for_products(response_data["results"])
        self.sort_results(response_data["results"], sort_filter)

        return response


class SearchProducts(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    product_view = ProductView()

    def get(self, request, *args, **kwargs):
        self.queryset = Product.objects.search(kwargs["query"])
        response = super().get(request, args, kwargs)
        response_data = response.data

        product_ids = []
        for product in response_data["results"]:
            product_ids.append(product["id"])

        response_data["results"] = self.product_view.get_by_ids(product_ids)
        return response


class ProductNetPrice(APIView):
    serializer_class = NetPriceSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,)

    def get(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            selling_price = serializer.data['selling_price']
            discount = serializer.data['discount']
            net_price_data = calculate_product_net_price(selling_price, discount)
            return Response({"results": net_price_data}, status=status.HTTP_200_OK)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProductSellerStatus(generics.ListAPIView):
    queryset = SellerProduct.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities |
                          IsEmployeeEntities)
    serializer_class = SellerProductSerializer

    def get(self, request, *args, **kwargs):
        input_serializer = GetBusinessClientProductsByStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get products", "errors": input_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        seller_ids = request.data["seller_ids"]
        activation_statuses = get_status(request.data['statuses'])
        self.check_object_permissions(request, seller_ids)

        self.queryset = SellerProduct.objects.select_related('product') \
            .filter(seller_id__in=seller_ids, product__activation_status__in=activation_statuses)
        response = super().get(request, args, kwargs)
        product_ids = []
        for seller_product in response.data["results"]:
            product_ids.append(seller_product["product"])
        response.data["results"] = ProductView().get_business_client_product_details(product_ids)

        return response


class GetSellerProductList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SellerProduct.objects.all()
    serializer_class = SellerProductSerializer

    def get(self, request, *args, **kwargs):
        seller_id = kwargs["seller_id"]
        self.check_object_permissions(request, seller_id)

        self.queryset = SellerProduct.objects.filter(seller_id=seller_id)
        response = super().get(request, args, kwargs)
        product_ids = []
        for seller_product in response.data["results"]:
            product_ids.append(seller_product["product"])
        response.data["results"] = ProductView().get_business_client_product_details(product_ids)

        return response


class ProductListBasedOnVerificationStatus(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    def get(self, request, *args, **kwargs):
        activation_status = self.kwargs['status']
        if activation_status not in [v_status.value for v_status in ActivationStatus]:
            return Response({"message": "Can't get product list",
                             "errors": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        self.queryset = Product.objects.filter(activation_status=activation_status).order_by("name")
        response = super().get(request, args, kwargs)
        add_verification_details_to_product(response.data["results"])
        return response


class ProductVerificationDetail(APIView):
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    def put(self, request, *args, **kwargs):
        try:
            product = Product.objects.get(id=self.kwargs['product_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Product verification", "error": "Invalid Product Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if product.activation_status == ActivationStatus.ACTIVE.value:
            return Response({"message": "Can't update Product verification",
                             "errors": "Product is already verified & active"}, status=status.HTTP_400_BAD_REQUEST)
        elif product.activation_status == ActivationStatus.DELETED.value:
            return Response({"message": "Can't update Product verification",
                             "errors": "Product is deleted"}, status=status.HTTP_400_BAD_REQUEST)

        input_serializer = ProductVerificationUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't update Product verification",
                             "errors": input_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        product_verification = ProductVerification.objects.get(product_id=self.kwargs['product_id'])
        request.data['product'] = product
        request.data['verified_by'] = request.user
        ProductVerificationSerializer().update(product_verification, request.data)

        activation_status = request.data['activation_status']
        if activation_status == ActivationStatus.ACTIVE.value:
            # updating verification details for product
            product.is_verified = True
            product.active_from = datetime.now()
        product.activation_status = activation_status
        product.save()

        return Response({"message": "Product verified successfully"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        product_verification = ProductVerification.objects.get(id=kwargs['product_id'])
        product_data = ProductView().get(product_verification.product)
        add_verification_details_to_product([product_data])
        return Response(product_data, 200)
