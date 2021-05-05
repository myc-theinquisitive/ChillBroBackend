from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category, CategoryImage
from rest_framework.response import Response
from .serializers import CategorySerializer, CategoryImageSerializer
from rest_framework.views import APIView
from collections import defaultdict
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsGet

class CategoryList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet, )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee | IsGet, )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee, )
    permission_classes = (IsAuthenticated,)
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer


class CategoryImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee, )
    permission_classes = (IsAuthenticated,)
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer


class CategoryTopLevelList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee | IsGet, )
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.filter(parent_category=None)
    serializer_class = CategorySerializer


def convert_category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_category_id": category.parent_category_id,
        "sub_categories": [],
        "images": []
    }




def recursive_category_grouping(group_categories_by_parent_id, group_images_by_category_id,
                                current_category_id, response):
    categories = group_categories_by_parent_id[current_category_id]
    for category in categories:
        category_id = category["id"]
        category["images"] = group_images_by_category_id[category_id]
        category.pop("parent_category_id")
        response.append(category)
        recursive_category_grouping(group_categories_by_parent_id, group_images_by_category_id,
                                    category_id, category["sub_categories"])


def get_category_details(parent_id):
    categories = Category.objects.all()
    category_images = CategoryImage.objects.all()

    group_categories_by_parent_id = defaultdict(list)
    for category in categories:
        group_categories_by_parent_id[category.parent_category_id].append(convert_category_to_dict(category))

    group_images_by_category_id = defaultdict(list)
    for category_image in category_images:
        if category_image.image and hasattr(category_image.image, 'url'):
            group_images_by_category_id[category_image.category_id].append(
                {
                    "id": category_image.id,
                    "image": category_image.image.url,
                    "order": category_image.order
                }
            )

    response = []
    recursive_category_grouping(group_categories_by_parent_id, group_images_by_category_id, parent_id, response)
    return response, group_images_by_category_id


class GetCategoriesLevelWise(APIView):

    def get(self, request, format=None):
        response_data, group_images_by_category_id = get_category_details(None)
        return Response(response_data, 200)


class GetSpecificCategoriesLevelWise(APIView):

    def get(self, request, *args, **kwargs):
        try:
            category = Category.objects.get(name__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Category!!!"}, 400)

        sub_categories, group_images_by_category_id = get_category_details(category.id)
        response_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "sub_categories": sub_categories,
            "images": group_images_by_category_id[category.id]
        }
        return Response(response_data, 200)
