from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer returns all data on Address from model"""
    class Meta:
        model = Address
        fields = '__all__'


class AddressIdListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )
