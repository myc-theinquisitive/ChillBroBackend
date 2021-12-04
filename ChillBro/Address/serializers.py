from rest_framework import serializers
from .models import Address, UserSavedAddress, Cities
from django.conf import settings


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer returns all data on Address from model"""
    class Meta:
        model = Address
        fields = '__all__'


class SavedAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSavedAddress
        fields = '__all__'


class AddressIdListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(max_length=36)
    )


class CitiesSerializer(serializers.ModelSerializer):
    """Address serializer returns all data on Address from model"""
    class Meta:
        model = Cities
        fields = '__all__'

    def to_representation(self, data):
        data = super(CitiesSerializer, self).to_representation(data)
        data['image_url'] = data.get('image_url').replace(settings.IMAGE_REPLACED_STRING, '')
        return data