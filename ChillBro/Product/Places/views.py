from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, PositiveIntegerField
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Place, PlaceImage
from .serializers import PlaceSerializer, PlaceImageSerializer, GetPlacesBySearchFilters
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from collections import defaultdict
from rest_framework.response import Response
from ..product_interface import ProductInterface
from typing import Dict
from .wrapper import get_address_details_for_address_ids, post_create_address, update_address_for_address_id, \
    filter_address_ids_by_city, average_rating_query_for_place, get_place_id_wise_average_rating
from decimal import Decimal
from Product.Category.models import Category


def add_address_details_to_places(places_list):
    address_ids = []
    for place in places_list:
        address_ids.append(place["address_id"])

    addresses = get_address_details_for_address_ids(address_ids)
    address_per_address_id = defaultdict(dict)
    for address in addresses:
        address_per_address_id[address["id"]] = address

    for place in places_list:
        address_id = place.pop("address_id", None)
        place["address"] = address_per_address_id[address_id]


def add_average_rating_for_places(places_response):
    place_ids = []
    for place in places_response:
        place_ids.append(place["id"])

    place_id_wise_rating = get_place_id_wise_average_rating(place_ids)
    for place in places_response:
        place["rating"] = place_id_wise_rating[place["id"]]


class PlaceView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.place_serializer = None
        self.place_object = None

        self.place_images = []
        self.address_data = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, place_data):
        place_object_defined = self.place_object is not None
        place_data_defined = place_data is not None

        if place_data_defined:
            if "images" in place_data:
                self.place_images = place_data.pop("images", [])
            self.address_data = place_data.pop("address", {})

        # for update
        if place_object_defined and place_data_defined:
            place_data["address_id"] = self.place_object.address_id
            self.place_serializer = PlaceSerializer(self.place_object, data=place_data)
        # for create
        elif place_data_defined:
            place_data["address_id"] = "Yet To ADD"
            self.place_serializer = PlaceSerializer(data=place_data)
        # for get
        elif place_object_defined:
            self.place_serializer = PlaceSerializer(self.place_object)
        else:
            self.place_serializer = PlaceSerializer()

    def validate_create_data(self, place_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(place_data)

        if not self.place_serializer.is_valid():
            is_valid = False
            errors["place"].append(self.place_serializer.errors)

        # Validating images
        place_image_serializer = PlaceImageSerializer(data=self.place_images, many=True)
        if not place_image_serializer.is_valid():
            is_valid = False
            errors["images"] = place_image_serializer.errors

        # Creating address here to validate
        # This should be the last validation
        address_details = post_create_address(self.address_data)
        if not address_details['is_valid']:
            is_valid = False
            errors["address"] = address_details['errors']
        else:
            self.address_data["id"] = address_details['address_id']

        return is_valid, errors

    def create(self, place_data):
        """
            {
                name: string,
                description: string,
                category: id-string,
                images: [
                    {
                        'image': file,
                        'order': int
                    }
                ],
                "address": {
                    "pincode": string,
                    "phone_number": string,
                    "city": string,
                    "state": string,
                    "country": string,
                    "name": string,
                    "address_line": string,
                    "extend_address": string,
                    "landmark": string,
                    "latitude": string,
                    "longitude": string
                },
            }
        """

        place_data["address_id"] = self.address_data["id"]
        place_object = self.place_serializer.create(place_data)

        # Add Images to Place
        place_image_dicts = []
        for image_dict in self.place_images:
            place_image_dict = {
                "place": place_object.id,
                "image": image_dict["image"],
                "order": image_dict["order"]
            }
            place_image_dicts.append(place_image_dict)
        PlaceImageSerializer.bulk_create(place_image_dicts)

        return {
            "id": place_object.id
        }

    def validate_update_data(self, place_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of vehicle to be updated
        try:
            self.place_object \
                = Place.objects.get(id=place_data["id"])
        except ObjectDoesNotExist:
            return False, {"errors": "Place does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(place_data)

        if not self.place_serializer.is_valid():
            is_valid = False
            errors.update(self.place_serializer.errors)

        address_details = update_address_for_address_id(self.place_object.address_id, self.address_data)
        if not address_details['is_valid']:
            is_valid = False
            errors["address"] = address_details['errors']
        return is_valid, errors

    def update(self, place_data):
        """
            {
                name: string,
                description: string,
                category: id-string,
                "address": {
                    "pincode": string,
                    "phone_number": string,
                    "city": string,
                    "state": string,
                    "country": string,
                    "name": string,
                    "address_line": string,
                    "extend_address": string,
                    "landmark": string,
                    "latitude": string,
                    "longitude": string
                },
            }
        """

        self.place_serializer.update(self.place_object, place_data)

    def get(self, place_id):
        self.place_object = Place.objects.get(id=place_id)
        self.initialize_product_class(None)

        place_data = self.place_serializer.data
        add_address_details_to_places([place_data])
        add_average_rating_for_places([place_data])
        return place_data

    def get_by_ids(self, place_ids):
        places = Place.objects.filter(id__in=place_ids)

        place_serializer = PlaceSerializer(places, many=True)
        places_data = place_serializer.data
        add_address_details_to_places(places_data)
        add_average_rating_for_places(places_data)
        return places_data


class PlaceList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    place_view = PlaceView()

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)

        place_ids = []
        for place in response.data["results"]:
            place_ids.append(place["id"])
        response.data["results"] = self.place_view.get_by_ids(place_ids)

        return response

    def post(self, request, *args, **kwargs):
        # TODO: remove when not using postman
        # request.data._mutable = True
        # request_data = request.data.dict()
        request_data = request.data

        is_valid, errors = self.place_view.validate_create_data(request_data)
        if not is_valid:
            return Response({"message": "Can't create place", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        response_data = self.place_view.create(request_data)
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class PlaceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    place_view = PlaceView()

    def get(self, request, *args, **kwargs):
        try:
            response_data = self.place_view.get(kwargs["pk"])
        except ObjectDoesNotExist:
            return Response({"errors": "Place does not Exist!!!"}, 400)

        return Response(data=response_data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        # TODO: remove when not using postman
        # request_data = request.data.dict()
        request_data = request.data
        request_data["id"] = kwargs["pk"]

        is_valid, errors = self.place_view.validate_update_data(request_data)
        if not is_valid:
            return Response({"message": "Place can't be updated", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        self.place_view.update(request_data)
        return Response({"message": "Place updated successfully"},
                        status=status.HTTP_200_OK)


class PlaceImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee, )
    queryset = PlaceImage.objects.all()
    serializer_class = PlaceImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            place = Place.objects.get(id=request.data['place'])
        except ObjectDoesNotExist:
            return Response({"errors": "Place does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.create(request.data)
        return Response({"message": "Place Image added successfully"}, status=status.HTTP_201_CREATED)


class PlaceImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee, )
    queryset = PlaceImage.objects.all()
    serializer_class = PlaceImageSerializer

    def delete(self, request, *args, **kwargs):
        try:
            product_image = PlaceImage.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"errors": "Place image does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)

        return super().delete(request, *args, **kwargs)


class GetPlacesByCategory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PlaceSerializer
    place_view = PlaceView()

    @staticmethod
    def apply_filters(category_ids, filter_data):
        # applying search and category filter
        if filter_data["search_text"]:
            filter_places = Place.objects.search(filter_data["search_text"]).filter(category_id__in=category_ids)
        else:
            filter_places = Place.objects.filter(category_id__in=category_ids)

        # applying location Filters
        location_filter = filter_data["location_filter"]
        if location_filter["applied"]:
            places_ids = filter_places.values_list("id", flat=True)
            address_ids = Place.objects.filter(id__in=places_ids).values_list("address_id", flat=True)
            city_address_ids = filter_address_ids_by_city(address_ids, location_filter["city"])
            city_place_ids = Place.objects.filter(
                address_id__in=city_address_ids, id__in=places_ids).values_list("id", flat=True)
            filter_places = filter_places.filter(id__in=city_place_ids)

        return filter_places.values_list("id", flat=True)

    @staticmethod
    def apply_sort_filter(query_set, sort_filter):
        if sort_filter == "AVERAGE_RATING":
            ratings_query = average_rating_query_for_place(OuterRef('id'))
            return query_set.annotate(
                average_rating=Subquery(
                    queryset=ratings_query,
                    output_field=PositiveIntegerField()
                )
            ).order_by('-average_rating')
        return query_set

    @staticmethod
    def sort_results(places_response, sort_filter):
        if sort_filter == "AVERAGE_RATING":
            places_response.sort(
                key=lambda place_response: Decimal(place_response['rating']['avg_rating']), reverse=True)

    def recursively_get_lower_level_categories(self, category_ids):
        if not category_ids:
            return []

        result_category_ids = category_ids
        next_level_category_ids = Category.objects.filter(parent_category_id__in=category_ids)\
            .values_list('id', flat=True)
        next_level_category_ids = list(next_level_category_ids)
        result_category_ids.extend(next_level_category_ids)

        recursive_category_ids = self.recursively_get_lower_level_categories(next_level_category_ids)
        result_category_ids.extend(recursive_category_ids)

        return list(set(result_category_ids))

    def get(self, request, *args, **kwargs):

        input_serializer = GetPlacesBySearchFilters(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get places", "errors": input_serializer.errors}, 400)

        try:
            category = Category.objects.get(name__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Category!!!"}, 400)
        all_category_ids = self.recursively_get_lower_level_categories([category.id])

        sort_filter = request.data["sort_filter"]
        place_ids = self.apply_filters(all_category_ids, request.data)
        self.queryset = Place.objects.filter(id__in=place_ids)
        self.queryset = self.apply_sort_filter(self.queryset, sort_filter)

        response = super().get(request, args, kwargs)
        response_data = response.data

        place_ids = []
        for place in response_data["results"]:
            place_ids.append(place["id"])
        response_data["results"] = self.place_view.get_by_ids(place_ids)

        # TODO: add wishlist status
        self.sort_results(response_data["results"], sort_filter)
        return response
