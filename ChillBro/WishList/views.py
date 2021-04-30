from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .wrapper import *
from .serializers import WishListSerializer, CreateWishListSerializer, UserWishListDetailsSerializer
from .models import *
from .helpers import getEntityType

# Create your views here.


class CreateWishList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = CreateWishListSerializer(data=request.data)
        if input_serializer.is_valid():
            previous_wishlist = WishList.objects.filter(user=request.user, product_id=request.data['product_id'])
            if len(previous_wishlist) > 0:
                return Response({"message": "You already added this product {}".format(request.data['product_id'])})

            entity_id, entity_type = getEntityDetailsOfProduct(request.data['product_id'])
            if entity_id is None and entity_type is None:
                return Response({"message": "Invalid Product Id {}".format(request.data['product_id'])},400)

            request.data['user'] = request.user
            serializer = WishListSerializer()
            wishlist = serializer.create(request.data)
            return Response({"message":"Product {} is successfully added to wishlist".format(request.data['product_id'])},200)
        else:
            return Response(input_serializer.errors, 400)


class UserWishListDetails(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        input_serializer = UserWishListDetailsSerializer(data=request.data)
        if input_serializer.is_valid():
            category_filters = getEntityType(request.data['category_filters'])

            wishlist = WishList.objects.filter(user = request.user, entity_type__in=category_filters)
            if len(wishlist) == 0:
                return Response({"message":"Sorry, There are no Wish Lists"},200)

            product_ids = []
            for each_wishlist in wishlist:
                product_ids.append(each_wishlist.product_id)
            product_details = get_product_details_with_image(product_ids)

            all_wish_list_products = []
            for each_wishlist in wishlist:
                each_wishlist_details = {'id': each_wishlist.id, 'entity_id': each_wishlist.entity_id,
                                         'entity_type': each_wishlist.entity_type, 'product_id': each_wishlist.product_id,
                                         'product_name': product_details[each_wishlist.product_id]['name'],
                                         'product_image_url': product_details[each_wishlist.product_id]['image_url'],
                                         'added_date': each_wishlist.date}
                all_wish_list_products.append(each_wishlist_details)
            return Response({"results":all_wish_list_products},200)
        else:
            return Response(input_serializer.errors, 400)


class DeletProductFromWishList(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer