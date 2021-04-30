from rest_framework import serializers
from .models import *

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = '__all__'

class EntityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in Status])

class BusinessClientEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientEntity
        fields = '__all__'

class AddressSerializer(serializers.Serializer):
    city=serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=6,validators=[MinLengthValidator(6)])