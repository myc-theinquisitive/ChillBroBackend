from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .wrapper import *
from .serializers import WishListSerializer, UserWishListDetailsSerializer,  AddItemToWishListSerializer
from .constants import *
from .models import *
from .helpers import get_entity_types
from django.core.exceptions import ObjectDoesNotExist


class AddItemToWishList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = AddItemToWishListSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't add the product to wishlist", "errors": input_serializer.errors}, 400)

        previous_wishlist = WishList.objects.filter(created_by=request.user, related_id=request.data['related_id'])
        if len(previous_wishlist) > 0:
            return Response({"message": "Can't add the product to wishlist",
                             "errors": "You already added this product to WishList"})
        item_type = request.data['item_type']
        if item_type == ItemType.PRODUCT.value:
            entity_id, entity_type = get_entity_details_of_product(request.data['related_id'])
            if entity_id is None and entity_type is None:
                return Response({"message": "Can't add the product to wishlist",
                                 "errors": "Invalid Related Id"}, 400)
            entity_sub_type = None
        elif item_type == ItemType.ENTITY.value:
            entity_type, entity_sub_type = get_entity_type_and_sub_type_for_entity_id(request.data['related_id'])
            if entity_type is None and entity_sub_type is None:
                return Response({"message": "Can't add entity to wishlist",
                                 "errors": "Invalid Entity Id"}, 400)

        elif item_type == ItemType.PLACE.value:
            entity_type, entity_sub_type = None, None

        request.data['created_by'] = request.user
        request.data['entity_type'] = entity_type
        request.data['entity_sub_type'] = entity_sub_type
        serializer = WishListSerializer()
        serializer.create(request.data)
        return Response({"message": "Product successfully added to wishlist"}, 200)


class DeleteItemFromWishList(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        try:
            delete_product = WishList.objects.get(created_by=request.user, related_id=kwargs['related_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't delete product", "errors": "Invalid related id"}, 400)

        delete_product.delete()
        return Response({"message": "Successfully deleted product from wishlist"}, 200)


class UserWishListDetails(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO: Handle entity case here
    def post(self, request, *args, **kwargs):
        input_serializer = UserWishListDetailsSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get the details of wishlist", "errors": input_serializer.errors}, 400)

        entity_type_filters = get_entity_types(request.data['entity_type_filters'])
        entity_sub_type_filters = get_entity_sub_types(request.data['entity_sub_type_filters'])

        if request.data['entity_sub_type_filters'] and request.data['entity_type_filters']:
            wishlist = WishList.objects.filter(
                created_by=request.user, entity_type__in=entity_type_filters,
                entity_sub_type__in=entity_sub_type_filters)
        elif request.data['entity_type_filters']:
            wishlist = WishList.objects.filter(
                created_by=request.user, entity_type__in=entity_type_filters)
        elif request.data['entity_sub_type_filters']:
            wishlist = WishList.objects.filter(
                created_by=request.user, entity_sub_type__in=entity_sub_type_filters)
        else:
            wishlist = WishList.objects.filter(created_by=request.user)

        if len(wishlist) == 0:
            return Response({"message": "Sorry, There are no Wish Lists"}, 200)

        product_ids = entity_ids = place_ids = []
        for each_wishlist in wishlist:
            if each_wishlist.item_type == ItemType.PRODUCT.value:
                product_ids.append(each_wishlist.related_id)
            elif each_wishlist.item_type == ItemType.ENTITY.value:
                entity_ids.append(each_wishlist.related_id)
            elif each_wishlist.item_type == ItemType.PLACE.value:
                place_ids.append(each_wishlist.related_id)

        product_id_wise_details = get_product_id_wise_details(product_ids)
        entity_id_wise_details = get_entity_id_wise_details(entity_ids)
        place_id_wise_details = get_place_id_wise_details(place_ids)

        all_wish_list_products = []
        for each_wishlist in wishlist:
            each_wishlist_details = {
                'id': each_wishlist.id,
                'related_id': each_wishlist.related_id,
                'entity_type': each_wishlist.entity_type,
                'entity_sub_type': each_wishlist.entity_sub_type,
                'item_type': each_wishlist.item_type,
                'added_date': each_wishlist.created_at
            }

            if each_wishlist.item_type == ItemType.PRODUCT.value:
                each_wishlist_details['product'] = product_id_wise_details[each_wishlist.related_id]

            elif each_wishlist.item_type == ItemType.ENTITY.value:
                each_wishlist_details['entity'] = entity_id_wise_details[each_wishlist.related_id]

            elif each_wishlist.item_type == ItemType.PLACE.value:
                each_wishlist_details['place'] = place_id_wise_details[each_wishlist.related_id]

            all_wish_list_products.append(each_wishlist_details)

        return Response({"results": all_wish_list_products}, 200)
