from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Category, CategoryImage, CategoryProductPrices, CategoryProduct
from rest_framework.response import Response
from .serializers import CategorySerializer, CategoryImageSerializer, CategoryProductSerializer, \
    CategoryProductPricesSerializer
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
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer


class CategoryImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee, )
    queryset = CategoryImage.objects.all()
    serializer_class = CategoryImageSerializer


class CategoryTopLevelList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee | IsGet, )
    queryset = Category.objects.filter(parent_category=None)
    serializer_class = CategorySerializer


def convert_category_to_dict(category):
    icon_url = category.icon_url
    # For thumbnails need to validate as it works in linux but not in windows
    # icon_url = category.icon_url.thumbnails.small.url
    icon_url = icon_url.url.replace(settings.IMAGE_REPLACED_STRING, "")

    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "parent_category_id": category.parent_category_id,
        "icon_url": icon_url,
        "sub_categories": [],
    }


def recursive_category_grouping(group_categories_by_parent_id, current_category_id, response):
    categories = group_categories_by_parent_id[current_category_id]
    for category in categories:
        category_id = category["id"]
        category.pop("parent_category_id")
        response.append(category)
        recursive_category_grouping(group_categories_by_parent_id, category_id, category["sub_categories"])


def get_category_details(parent_id):
    categories = Category.objects.all()

    group_categories_by_parent_id = defaultdict(list)
    for category in categories:
        group_categories_by_parent_id[category.parent_category_id].append(convert_category_to_dict(category))

    response = []
    recursive_category_grouping(group_categories_by_parent_id, parent_id, response)
    return response


class GetCategoriesLevelWise(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        response_data = get_category_details(None)
        return Response({"results": response_data}, 200)


class GetSpecificCategoriesLevelWise(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        try:
            category = Category.objects.get(name__icontains=kwargs["slug"])
        except ObjectDoesNotExist:
            return Response({"errors": "Invalid Category!!!"}, 400)

        sub_categories = get_category_details(category.id)
        slug_value = kwargs['slug'].lower()
        if slug_value == 'transport':
            new_sub_categories = []
            for each_category in sub_categories:
                if each_category['name'].lower() == 'place' or each_category['name'].lower() == 'vehicles':
                    pass
                else:
                    new_sub_categories.append(each_category)
            response_data = convert_category_to_dict(category)
            response_data["sub_categories"] = new_sub_categories
        else:
            response_data = convert_category_to_dict(category)
            response_data["sub_categories"] = sub_categories

        return Response(response_data, 200)


class CategoryProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee)
    queryset = CategoryProduct.objects.all()
    serializer_class = CategoryProductSerializer


class CategoryProductDetail(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee)
    queryset = CategoryProductPrices.objects.all()
    serializer_class = CategoryProductPricesSerializer


class CategoryProductPricesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,  IsSuperAdminOrMYCEmployee)
    queryset = CategoryProductPrices.objects.all()
    serializer_class = CategoryProductPricesSerializer


class CategoryProductPricesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CategoryProductPrices.objects.all()
    serializer_class = CategoryProductPricesSerializer

    def get(self, request, *args, **kwargs):
        try:
            prices = CategoryProductPrices.objects.get(category_product=kwargs['category_product'])
        except ObjectDoesNotExist:
            return Response({"min_price": -1, "max_price": -1, "min_discount": -1, "max_discount": -1}, 400)

        serializer = self.serializer_class(prices)
        return Response(serializer.data, 200)

    def put(self, request, *args, **kwargs):
        prices = CategoryProductPrices.objects.filter(category=kwargs['category_product'])
        if len(prices) == 0:
            return Response({"message": "Can't edit the category product",
                             "errors": "Category product prices doesn't exit"}, 400)

        prices.update(min_price=request.data['min_price'], max_price=request.data['max_price'],
                      min_discount=request.data['min_discount'], max_discount=request.data['max_discount'])
        return Response({"message": "Successfully edited the category product prices"}, 200)

    def delete(self, request, *args, **kwargs):
        prices = CategoryProductPrices.objects.filter(category=kwargs['category_product'])
        if len(prices) == 0:
            return Response({"message": "Can't delete the category product",
                             "errors": "Category product Prices doesn't exit"}, 400)

        prices.delete()
        return Response({"message": "Successfully deleted category product prices"}, 200)


class GetVehiclesCategoriesList(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        vehicles_categories = Category.objects.filter(parent_category__name__icontains="vehicles")
        vehicle_details = []
        for each_vehicle in vehicles_categories:
            icon_url = each_vehicle.icon_url.url.replace(settings.IMAGE_REPLACED_STRING, "")
            vehicle_details.append({
                'id': each_vehicle.id,
                'name': each_vehicle.name,
                'image': icon_url
            })
        return Response({"results":vehicle_details},200)

class GenerateKey(APIView):

    def get(self, request,*args, **kwargs):
        categories = Category.objects.all()
        print(categories)
        for each_category in categories:
            key = each_category.name.lower().split()
            each_category.key = "-".join(key)
            each_category.save()

        return Response({"message":"successfully generated"},200)