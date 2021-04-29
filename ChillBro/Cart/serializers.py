from rest_framework import serializers
from .models import *


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProducts
        fields = '__all__'


class CreateCartSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True, min_length=36, max_length=36)
    quantity = serializers.IntegerField(required=True)
    start_time = serializers.DateTimeField(required=True)
    end_time = serializers.DateTimeField(required=True)



