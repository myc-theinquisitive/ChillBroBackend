import json
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Subquery, OuterRef, PositiveIntegerField
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .BaseProduct.serializers import ProductVerificationSerializer, ProductVerificationUpdateInputSerializer
from .Driver.models import Driver, VehiclesDrivenByDriver
from .HireAVehicle.models import HireAVehicle
from .product_view import ProductView
from .serializers import ProductSerializer, IdsListSerializer, NetPriceSerializer, \
    GetProductsBySearchFilters, GetBusinessClientProductsByStatusSerializer
from .wrapper import filter_seller_ids_by_city, average_rating_query_for_product, get_product_id_wise_average_rating, \
    get_product_id_wise_wishlist_status, get_rating_wise_review_details_for_product, \
    get_rating_type_wise_average_rating_for_product, get_latest_ratings_for_product
from rest_framework import status, generics
from .constants import COMMISION_FEE_PERCENT, TRANSACTION_FEE_PERCENT, GST_PERCENT, FIXED_FEE_PERCENT
from .BaseProduct.models import Product, ProductVerification
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsOwnerById, IsUserOwner, IsSellerProduct, \
    IsBusinessClientEntities, IsEmployeeEntities
from .BaseProduct.constants import ActivationStatus, ProductTypes
from datetime import datetime
from .helpers import get_date_format, get_status
from decimal import Decimal
from rest_framework.response import Response
from .Category.models import Category
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from datetime import date

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def get_invalid_product_ids(product_ids):
    existing_product_ids = Product.objects.filter(id__in=product_ids).values_list("id", flat=True)
    return set(product_ids) - set(existing_product_ids)


def add_average_rating_for_products(products_response):
    product_ids = []
    for product in products_response:
        product_ids.append(product["id"])

    product_id_wise_rating = get_product_id_wise_average_rating(product_ids)
    for product in products_response:
        product["rating"] = product_id_wise_rating[product["id"]]


def add_wishlist_status_for_products(user_id, products_response):
    product_ids = []
    for product in products_response:
        product_ids.append(product["id"])

    product_id_wise_wishlist_status = get_product_id_wise_wishlist_status(user_id, product_ids)
    for product in products_response:
        product["in_wishlist"] = product_id_wise_wishlist_status[product["id"]]


def calculate_net_price(final_selling_price, product_type):
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


def calculate_product_net_price(selling_price, discount):
    final_selling_price = selling_price - (selling_price * discount) / 100
    return calculate_net_price(final_selling_price, "product type")


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
        request.data['created_by'] = request.user.id
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
        request.data['created_by'] = request.user.id
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

        add_wishlist_status_for_products(request.user.id, [response_data])
        rating_stats = get_rating_wise_review_details_for_product(id)
        rating_type_stats = get_rating_type_wise_average_rating_for_product(id)
        reviews_list = get_latest_ratings_for_product(id)
        response_data["reviews"] = {
            "rating_stats": rating_stats,
            "rating_type_stats": rating_type_stats,
            "review_list": reviews_list
        }
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
    def apply_filters(category_ids, filter_data):
        # applying category filter
        filter_products = Product.objects.filter(category_id__in=category_ids).active()
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
            seller_ids = Product.objects.filter(product_id__in=product_ids).values_list("seller_id", flat=True)
            city_seller_ids = filter_seller_ids_by_city(seller_ids, location_filter["city"])
            city_product_ids = Product.objects.filter(
                seller_id__in=city_seller_ids, product_id__in=product_ids).values_list("product_id", flat=True)
            filter_products = filter_products.filter(id__in=city_product_ids)

        transport_filter = filter_data["transport_filter"]
        if transport_filter["hire_a_driver"]["applied"]:
            product_ids = filter_products.values_list("id", flat=True)
            todays_date = date.today()
            current_year = todays_date.year
            max_year = current_year - transport_filter["hire_a_driver"]["min_experience"]
            if transport_filter['hire_a_driver']['max_experience']:
                min_year = current_year - transport_filter["hire_a_driver"]["max_experience"]
            else:
                min_year = 0

            drivers_filter_by_experience = Driver.objects.filter(
                product_id__in=product_ids, licensed_from__gte=min_year, licensed_from__lt=max_year)
            drivers_filter_product_ids = drivers_filter_by_experience.values_list("product_id", flat=True)

            if transport_filter['hire_a_driver']['vehicle_category']:
                vehicle_driven_by_drivers = VehiclesDrivenByDriver.objects.select_related('category')\
                    .filter(product_id__in=drivers_filter_product_ids,
                            category__name=transport_filter['hire_a_driver']['vehicle_category'])
                vehicle_driven_product_ids = vehicle_driven_by_drivers.values_list("product_id", flat=True)
                filter_products = filter_products.filter(id__in=vehicle_driven_product_ids)
            else:
                filter_products = filter_products.filter(id__in=drivers_filter_product_ids)

        if transport_filter["hire_a_vehicle"]["applied"]:
            if transport_filter["hire_a_vehicle"]["vehicle_category"]:
                product_ids = filter_products.values_list("id", flat=True)
                vehicle_category = HireAVehicle.objects.select_related("vehicle")\
                    .filter(product_id__in=product_ids,
                            vehicle__category__name=transport_filter["hire_a_vehicle"]["vehicle_category"])
                vehicle_product_ids = vehicle_category.values_list("product_id", flat=True)
                filter_products = filter_products.filter(id__in=vehicle_product_ids)

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
                key=lambda product_response: Decimal(product_response['rating']['avg_rating']), reverse=True)

    def recursively_get_lower_level_categories(self, category_ids):
        if not category_ids:
            return []

        result_category_ids = category_ids
        next_level_category_ids = Category.objects.filter(parent_category_id__in=category_ids) \
            .values_list('id', flat=True)
        next_level_category_ids = list(next_level_category_ids)
        result_category_ids.extend(next_level_category_ids)

        recursive_category_ids = self.recursively_get_lower_level_categories(next_level_category_ids)
        result_category_ids.extend(recursive_category_ids)

        return list(set(result_category_ids))

    def get(self, request, *args, **kwargs):
        input_serializer = GetProductsBySearchFilters(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get products", "errors": input_serializer.errors}, 400)

        # adding inputs other than request body data
        request.data["category"] = kwargs["slug"]
        request.data["page"] = request.query_params.get('page')
        cache_key = json.dumps(request.data)
        if cache_key in {}:
            response_data = cache.get(cache_key)
        else:
            try:
                category = Category.objects.get(name__icontains=kwargs["slug"])
            except ObjectDoesNotExist:
                return Response({"errors": "Invalid Category!!!"}, 400)

            all_category_ids = self.recursively_get_lower_level_categories([category.id])
            sort_filter = request.data["sort_filter"]
            product_ids = self.apply_filters(all_category_ids, request.data)
            self.queryset = Product.objects.filter(id__in=product_ids)
            self.queryset = self.apply_sort_filter(self.queryset, sort_filter)

            response = super().get(request, args, kwargs)
            response_data = response.data

            product_ids = []
            for product in response_data["results"]:
                product_ids.append(product["id"])
            response_data["results"] = self.product_view.get_by_ids(product_ids)
            self.sort_results(response_data["results"], sort_filter)
            # cache.set(cache_key, response_data, timeout=CACHE_TTL)

        add_wishlist_status_for_products(request.user.id, response_data["results"])
        return Response(response_data)


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
        if not serializer.is_valid():
            return Response({"message": "Can't get Net Price", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        selling_price = serializer.data['selling_price']
        discount = serializer.data['discount']
        net_price_data = calculate_product_net_price(selling_price, discount)
        return Response({"results": net_price_data}, status=status.HTTP_200_OK)


class BusinessClientProductsByVerificationStatus(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntities |
                          IsEmployeeEntities)
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        input_serializer = GetBusinessClientProductsByStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get products", "errors": input_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        seller_ids = request.data["seller_ids"]
        activation_statuses = get_status(request.data['statuses'])
        self.check_object_permissions(request, seller_ids)

        self.queryset = Product.objects.filter(seller_id__in=seller_ids, activation_status__in=activation_statuses)
        response = super().get(request, args, kwargs)

        product_ids = []
        for product in response.data["results"]:
            product_ids.append(product["id"])
        response.data["results"] = ProductView().get_business_client_product_details(product_ids)
        return response


class GetSellerProductList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, *args, **kwargs):
        seller_id = kwargs["seller_id"]
        self.check_object_permissions(request, seller_id)

        self.queryset = Product.objects.filter(seller_id=seller_id)
        response = super().get(request, args, kwargs)

        product_ids = []
        for product in response.data["results"]:
            product_ids.append(product["id"])
        response.data["results"] = ProductView().get_by_ids(product_ids)

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
                             "errors": "Product deleted"}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(product_data, status=status.HTTP_200_OK)


class RentalHomePageCategories(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        product_ids = Product.objects.filter(type=ProductTypes.Rental.value).values_list('id', flat=True)

        rental_products_details = ProductView().get_by_ids(product_ids)
        rental_categories_home_page = defaultdict(list)

        count = 0
        for each_product in product_ids:
            if count % 4 == 0:
                rental_categories_home_page['Best Valued'].append(rental_products_details[count])
            if count % 4 == 1:
                rental_categories_home_page["Combo's"].append(rental_products_details[count])
            if count % 4 == 2:
                rental_categories_home_page['Seasonal Rentals'].append(rental_products_details[count])
            if count % 4 == 3:
                rental_categories_home_page['New Arrivals'].append(rental_products_details[count])
            count += 1

        rental_home_page_categories = [{
            'name': 'Best Valued',
            'products': rental_categories_home_page['Best Valued']
        }, {
            'name': "Combo's",
            'products': rental_categories_home_page["Combo's"]
        }, {
            'name': 'Seasonal Rentals',
            'products': rental_categories_home_page['Seasonal Rentals']
        }, {
            'name': 'New Arrivals',
            'products': rental_categories_home_page['New Arrivals']
        }]

        return Response({"results": rental_home_page_categories}, 200)


class RentalProductsTypes(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        rental_products_types = ["Best Valued", "Combo's", "Seasonal Rentals", "New Arrivals"]

        return Response({"results": rental_products_types}, 200)


class HotelEntityProducts(generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        product_ids = Product.objects.filter(seller_id=kwargs['seller_id']).values_list('id', flat=True)

        hotel_products_details = ProductView().get_by_ids(product_ids)

        return Response({"results": hotel_products_details}, 200)


class HotelProductsTypes(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        hotel_products_types = ["Near By You", "Trending", "Budget", "All Hotels"]

        return Response({"results": hotel_products_types}, 200)


class HireADriverHomePage(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        driver_product_ids = Product.objects.filter(type=ProductTypes.Driver.value).values_list("id", flat=True)

        driver_details = ProductView().get_by_ids(driver_product_ids)
        driver_products = defaultdict(list)
        todays_date = date.today()
        current_year = todays_date.year
        for each_driver in driver_details:
            experience = current_year - each_driver["driver"]["licensed_from"]
            if experience >= 15:
                driver_products[">15"].append(each_driver)
            elif 10 <= experience < 15:
                driver_products["10-15"].append(each_driver)
            elif 5 <= experience < 10:
                driver_products["5-10"].append(each_driver)
            elif 0 <= experience < 5:
                driver_products["0-5"].append(each_driver)

        hire_a_driver_home_page_products = [{
            "name": ">15",
            "products": driver_products[">15"]
        }, {
            "name": "10-15",
            "products": driver_products["10-15"]
        }, {
            "name": "5-10",
            "products": driver_products["5-10"]
        }, {
            "name": "0-5",
            "products": driver_products["0-5"]
        }]

        return Response({"results": hire_a_driver_home_page_products}, 200)


class HireADriverYearsFilter(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        hire_a_driver_experience_filter = [
            {"max": None, "min": 15},
            {"max": 15, "min": 10},
            {"max": 10, "min": 5},
            {"max": 5, "min": 0}]

        return Response({"results": hire_a_driver_experience_filter}, 200)
