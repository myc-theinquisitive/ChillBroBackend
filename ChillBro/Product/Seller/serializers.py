from rest_framework import serializers
from .models import SellerProduct


class SellerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProduct
        fields = '__all__'