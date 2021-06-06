from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import Place, PlaceImage
from .serializers import PlaceSerializer, PlaceImageSerializer
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from collections import defaultdict
from rest_framework.response import Response
from ..product_interface import ProductInterface
from typing import Dict


class PlaceView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.place_serializer = None
        self.place_object = None
        self.place_images = []

    # initialize the instance variables before accessing
    def initialize_product_class(self, place_data):
        place_object_defined = self.place_object is not None
        place_data_defined = place_data is not None

        if place_data_defined and "images" in place_data:
            self.place_images = place_data.pop("images", [])

        # for update
        if place_object_defined and place_data_defined:
            self.place_serializer = PlaceSerializer(self.place_object, data=place_data)
        # for create
        elif place_data_defined:
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
                ]
            }
        """

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

        return is_valid, errors

    def update(self, place_data):
        """
            {
                name: string,
                description: string,
                category: id-string,
            }
        """

        self.place_serializer.update(self.place_object, place_data)

    def get(self, place_id):
        self.place_object = Place.objects.get(id=place_id)
        self.initialize_product_class(None)

        place_data = self.place_serializer.data
        return place_data

    def get_by_ids(self, place_ids):
        places = Place.objects.filter(id__in=place_ids)

        place_serializer = PlaceSerializer(places, many=True)
        places_data = place_serializer.data
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
