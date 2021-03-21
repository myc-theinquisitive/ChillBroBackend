from .Category.views import *
from .BaseProduct.views import *
from .Hotel.views import *
from .product_interface import ProductInterface
from .serializers import ProductSerializer, IdsListSerializer
from .Hotel.views import HotelView
from collections import defaultdict


class ProductView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.product_serializer = None
        self.product_specific_serializer = None

        self.product_specific_view = None
        self.product_specific_key = None
        self.product_specific_data = None

        self.product_object = None

    @staticmethod
    def get_view_and_key_by_type(product_type):
        if product_type == "Hotel":
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
                = Product.objects.get(slug=product_data["slug"])
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

        slug = response.pop("slug", None)
        response["url"] = "product/" + slug

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

    def get(self, product_slug):

        self.product_object = Product.objects.get(slug=product_slug)
        self.initialize_product_class(None)

        product_data = self.product_serializer.data
        product_data = self.update_product_response(product_data)

        product_id_wise_images_dict = self.get_product_id_wise_images([self.product_object.id])
        product_data["images"] = product_id_wise_images_dict[self.product_object.id]

        product_specific_data = self.product_specific_view.get(self.product_object.id)
        product_data[self.product_specific_key] = product_specific_data

        return product_data

    def get_by_ids(self, product_ids):

        products = Product.objects.filter(id__in=product_ids)

        products_serializer = ProductSerializer(products, many=True)
        products_data = products_serializer.data

        product_id_wise_images_dict = self.get_product_id_wise_images(product_ids)

        group_products_by_type = defaultdict(list)
        for product_data in products_data:
            product_data = self.update_product_response(product_data)
            product_data["images"] = product_id_wise_images_dict[product_data["id"]]
            group_products_by_type[product_data["type"]].append(product_data)

        response = []
        for type in group_products_by_type:
            product_view, product_key = self.get_view_and_key_by_type(type)

            product_specific_ids = []
            for product_dict in group_products_by_type[type]:
                product_specific_ids.append(product_dict["id"])

            product_specific_data = product_view.get_by_ids(product_specific_ids)

            # combine product data with product specific data
            product_id_product_specific_data_dict = {}
            for product_specific_dict in product_specific_data:
                product_id_product_specific_data_dict[product_specific_dict["id"]] = product_specific_dict

            for product_dict in group_products_by_type[type]:
                product_dict[product_key] = product_id_product_specific_data_dict[product_dict["id"]]
                response.append(product_dict)

        return products_data


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

    def put(self, request, slug):
        request.data["slug"] = slug

        is_valid, errors = self.product_view.validate_update_data(request.data)
        if not is_valid:
            return Response(errors, 400)

        response_data = self.product_view.update(request.data)
        return Response(data=response_data, status=201)

    def get(self, request, slug, format=None, *args):
        try:
            response_data = self.product_view.get(slug)
        except ObjectDoesNotExist:
            return Response({"errors": "Product does not Exist!!!"}, 400)

        return Response(data=response_data, status=200)


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
