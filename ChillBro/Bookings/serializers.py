from rest_framework import serializers
from .models import *


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProducts
        fields = '__all__'
