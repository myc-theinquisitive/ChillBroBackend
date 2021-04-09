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
    def bulk_create(self, validated_data):
        print(validated_data)
        for i in validated_data:
            print(i)
            super().create(i)
            # print("came"+i)
        return True

