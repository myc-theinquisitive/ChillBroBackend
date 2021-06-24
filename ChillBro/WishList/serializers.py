from rest_framework import serializers
from .models import *


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'


class AddItemToWishListSerializer(serializers.Serializer):
    related_id = serializers.CharField(required=True, min_length=36, max_length=36)
    item_type = serializers.CharField(required=True)


class UserWishListDetailsSerializer(serializers.Serializer):
    entity_type_filters = serializers.ListField(
        child=serializers.CharField()
    )
    entity_sub_type_filters = serializers.ListField(
        child=serializers.CharField()
    )
