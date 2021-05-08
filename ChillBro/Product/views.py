from .Category.views import *
from .BaseProduct.views import *
from .Hotel.views import *
from .Seller.views import *
from .product_interface import ProductInterface
from .serializers import ProductSerializer, IdsListSerializer, SellerProductSerializer, NetPriceSerializer, ProductQuantitySerializer
from .Hotel.views import HotelView
from collections import defaultdict
from .wrapper import key_value_content_type_model, key_value_tag_model, check_entity_id_is_exist, \
    get_booked_count_of_product_id
from .models import SellerProduct
from rest_framework import status
from .constants import COMMISION_FEE_PERCENT, TRANSACTION_FEE_PERCENT, GST_PERCENT, FIXED_FEE_PERCENT
from .BaseProduct.models import Product
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsOwnerById, IsUserOwner, IsSellerProduct, IsEmployeeBusinessClient
from .BaseProduct.constants import ProductStatus
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

        self.key_value_content_type_model = key_value_content_type_model()
        self.key_value_tag_model = key_value_tag_model()

    @staticmethod
    def get_view_and_key_by_type(product_type):
        if product_type == "HOTEL":
            return HotelView(), "hotel_room"
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

        # Entity details validation
        if "entity_id" not in product_data:
            is_valid = False
            errors["entity_id"].append("This field is required")
        else:
            entity_id = product_data["entity_id"]
            check_entity_id = check_entity_id_is_exist(entity_id)
            if not check_entity_id['is_valid']:
                is_valid = False
                errors["entity_id"].append("Invalid Entity Id")

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
            'active': boolean,
            'tags': ['hotel', 'stay'],
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
            'active': boolean,
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

        return response

    @staticmethod
    def get_product_id_wise_images(product_ids):
        product_images = ProductImage.objects.filter(product_id__in=product_ids)

        product_id_wise_images_dict = defaultdict(list)
        for product_image in product_images:
            product_id_wise_images_dict[product_image.product_id].append(
                {
                    "id": product_image.id,
                    "image": product_image.image.url,
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

        product_id_wise_sellers_dict = defaultdict(list)
        for product_seller in product_sellers:
            product_id_wise_sellers_dict[product_seller.product_id].append(
                {
                    "seller_id": product_seller.seller_id
                }
            )
        return product_id_wise_sellers_dict

    def get(self, product_id):
        self.product_object = Product.objects.get(id=product_id)
        self.initialize_product_class(None)

        product_data = self.product_serializer.data
        product_data = self.update_product_response(product_data)

        product_id_wise_features_dict = self.get_product_id_wise_features([self.product_object.id])
        product_data["features"] = product_id_wise_features_dict[self.product_object.id]

        product_id_wise_images_dict = self.get_product_id_wise_images([self.product_object.id])
        product_data["images"] = product_id_wise_images_dict[self.product_object.id]

        product_id_wise_sellers_dict = self.get_product_id_wise_sellers([self.product_object.id])
        product_data["sellers"] = product_id_wise_sellers_dict[self.product_object.id]

        product_specific_data = self.product_specific_view.get(self.product_object.id)
        product_specific_data.pop("product", None)
        product_data[self.product_specific_key] = product_specific_data

        return product_data

    def get_by_ids(self, product_ids):

        products = Product.objects.filter(id__in=product_ids)

        products_serializer = ProductSerializer(products, many=True)
        products_data = products_serializer.data

        product_id_wise_images_dict = self.get_product_id_wise_images(product_ids)
        product_id_wise_features_dict = self.get_product_id_wise_features(product_ids)
        product_id_wise_sellers_dict = self.get_product_id_wise_sellers(product_ids)

        group_products_by_type = defaultdict(list)
        for product_data in products_data:
            product_data = self.update_product_response(product_data)
            product_data["features"] = product_id_wise_features_dict[product_data["id"]]
            product_data["images"] = product_id_wise_images_dict[product_data["id"]]
            product_data["sellers"] = product_id_wise_sellers_dict[product_data["id"]]
            group_products_by_type[product_data["type"]].append(product_data)

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

    @staticmethod
    def get_business_client_product_details(product_ids):
        products = Product.objects.filter(id__in=product_ids)
        product_id_wise_images = ProductView().get_product_id_wise_images(product_ids)

        today_date = date.today()
        tomorrow_date = today_date + timedelta(1)

        products_data = []
        for product in products:
            images = product_id_wise_images[product.id]

            total_booked = get_booked_count_of_product_id(product.id, today_date, tomorrow_date)
            discount = ((product.price - product.discounted_price) / product.price) * 100
            net_price_data = calculate_product_net_price(product.price, discount)

            product_details = {
                'product_id': product.id,
                'name': product.name,
                'description': product.description,
                'images': images,
                'bookings': {
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
            return Response(response_data, 200)
        else:
            return Response(serializer.errors, 400)


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
        product.status = ProductStatus.DELETED.value
        product.save()
        return Response({"success": "Deleted Successfully"}, status=status.HTTP_200_OK)


class GetProductsByCategory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProductSerializer
    product_view = ProductView()

    def get(self, request, *args, **kwargs):
        try:
            category = Category.objects.get(name__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Category!!!"}, 400)

        self.queryset = Product.objects.filter(category_id=category.id)
        response = super().get(request, args, kwargs)
        response_data = response.data

        product_ids = []
        for product in response_data["results"]:
            product_ids.append(product["id"])

        response_data["results"] = self.product_view.get_by_ids(product_ids)

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
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, )

    def get(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            selling_price = serializer.data['selling_price']
            discount = serializer.data['discount']
            net_price_data = calculate_product_net_price(selling_price, discount)
            return Response(net_price_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductSellerStatus(generics.ListAPIView):
    queryset = SellerProduct.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | (IsBusinessClient & IsOwnerById) |
                          IsSellerProduct | IsEmployeeBusinessClient)
    serializer_class = SellerProductSerializer

    def get(self, request, *args, **kwargs):
        seller_id = kwargs["seller_id"]
        status = kwargs['status']
        self.check_object_permissions(request, seller_id)

        self.queryset = SellerProduct.objects.select_related('product')\
            .filter(seller_id=seller_id, product__status=status)
        response = super().get(request, args, kwargs)
        product_ids = []
        for seller_product in response.data["results"]:
            product_ids.append(seller_product["product"])
        response.data["results"] = ProductView().get_business_client_product_details(product_ids)

        return response


class GetSellerProductList(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
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


class ProductQuantity(APIView):
    serializer_class = ProductQuantitySerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | (IsBusinessClient & IsOwnerById) |
                          IsSellerProduct | IsEmployeeBusinessClient)

    def put(self, request, product_id):
        products = Product.objects.filter(id=product_id)
        if len(products) != 1:
            return Response({"message": "Invalid Product id"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, product_id)

        if request.data["quantity"] <= 0:
            return Response({"message": "Can't update product quantity",
                             "error": "Quantity should be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        products.update(quantity=request.data["quantity"])
        return Response({"message": "Updated Successfully"}, status=status.HTTP_200_OK)
