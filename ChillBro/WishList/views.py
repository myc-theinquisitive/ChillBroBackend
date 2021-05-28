from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .wrapper import *
from .serializers import WishListSerializer, AddProductToWishListSerializer, UserWishListDetailsSerializer, \
    AddEntityToWishListSerializer
from .models import *
from .helpers import get_entity_types
from django.core.exceptions import ObjectDoesNotExist


class AddProductToWishList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddProductToWishListSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add the product to wishlist", "errors": input_serializer.errors}, 400)

        previous_wishlist = WishList.objects.filter(created_by=request.user, product_id=request.data['product_id'])
        if len(previous_wishlist) > 0:
            return Response({"message": "Can't add the product to wishlist",
                             "errors": "You already added this product to WishList"})

        entity_id, entity_type = get_entity_details_of_product(request.data['product_id'])
        if entity_id is None and entity_type is None:
            return Response({"message": "Can't add the product to wishlist",
                             "errors": "Invalid Product Id"}, 400)

        request.data['created_by'] = request.user
        request.data['entity_id'] = entity_id
        request.data['entity_type'] = entity_type
        request.data['item_type'] = ItemType.PRODUCT.value
        serializer = WishListSerializer()
        serializer.create(request.data)
        return Response({"message": "Product successfully added to wishlist"}, 200)


class DeleteProductFromWishList(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            delete_product = WishList.objects.get(created_by=request.user, product_id=kwargs['product_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't delete product", "errors": "Invalid product id"}, 400)

        delete_product.delete()
        return Response({"message": "Successfully deleted product from wishlist"}, 200)


class AddEntityToWishList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddEntityToWishListSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add entity to wishlist", "errors": input_serializer.errors}, 400)

        previous_wishlist = WishList.objects.filter(
            created_by=request.user, entity_id=request.data['entity_id'], item_type=ItemType.ENTITY.value)
        if len(previous_wishlist) > 0:
            return Response({"message": "Can't add entity to wishlist",
                             "errors": "You already added this entity to WishList"})

        entity_type, entity_sub_type = get_entity_type_and_sub_type_for_entity_id(request.data['entity_id'])
        if entity_type is None and entity_sub_type is None:
            return Response({"message": "Can't add entity to wishlist",
                             "errors": "Invalid Entity Id"}, 400)

        request.data['created_by'] = request.user
        request.data['entity_type'] = entity_type
        request.data['entity_sub_type'] = entity_sub_type
        request.data['item_type'] = ItemType.ENTITY.value
        serializer = WishListSerializer()
        serializer.create(request.data)
        return Response({"message": "Entity successfully added to wishlist"}, 200)


class DeleteEntityFromWishList(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            delete_entity = WishList.objects.get(
                created_by=request.user, entity_id=kwargs['entity_id'], item_type=ItemType.ENTITY.value)
        except ObjectDoesNotExist:
            return Response({"message": "Can't delete entity", "errors": "Invalid entity id"}, 400)

        delete_entity.delete()
        return Response({"message": "Successfully deleted entity from wishlist"}, 200)


class UserWishListDetails(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO: Handle entity case here
    def post(self, request, *args, **kwargs):
        input_serializer = UserWishListDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get the details of wishlist", "errors": input_serializer.errors}, 400)

        entity_type_filters = get_entity_types(request.data['entity_type_filters'])
        entity_sub_type_filters = get_entity_sub_types(request.data['entity_sub_type_filters'])

        if request.data['entity_sub_type_filters']:
            wishlist = WishList.objects.filter(
                created_by=request.user, entity_type__in=entity_type_filters,
                entity_sub_type__in=entity_sub_type_filters)
        else:
            wishlist = WishList.objects.filter(
                created_by=request.user, entity_type__in=entity_type_filters)

        if len(wishlist) == 0:
            return Response({"message": "Sorry, There are no Wish Lists"}, 200)

        product_ids = []
        entity_ids = []
        for each_wishlist in wishlist:
            if each_wishlist.item_type == ItemType.PRODUCT.value:
                product_ids.append(each_wishlist.product_id)
            elif each_wishlist.item_type == ItemType.ENTITY.value:
                entity_ids.append(each_wishlist.entity_id)

        product_id_wise_details = get_product_id_wise_details(product_ids)
        entity_id_wise_details = get_entity_id_wise_details(entity_ids)

        all_wish_list_products = []
        for each_wishlist in wishlist:
            each_wishlist_details = {
                'id': each_wishlist.id,
                'entity_id': each_wishlist.entity_id,
                'entity_type': each_wishlist.entity_type,
                'entity_sub_type': each_wishlist.entity_sub_type,
                'item_type': each_wishlist.item_type,
                'added_date': each_wishlist.created_at
            }
            all_wish_list_products.append(each_wishlist_details)

            if each_wishlist.item_type == ItemType.PRODUCT.value:
                each_wishlist_details['product'] = product_id_wise_details[each_wishlist.product_id]

            elif each_wishlist.item_type == ItemType.ENTITY.value:
                each_wishlist_details['entity'] = entity_id_wise_details[each_wishlist.entity_id]

        return Response({"results": all_wish_list_products}, 200)
