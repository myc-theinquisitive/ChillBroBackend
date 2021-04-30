from rest_framework import serializers
from .models import *


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'


class CreateWishListSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)


class UserWishListDetailsSerializer(serializers.Serializer):
    category_filters = serializers.ListField(
        child=serializers.CharField()
    )