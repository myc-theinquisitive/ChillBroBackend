from rest_framework import serializers
from .models import *


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = '__all__'
        read_only_fields = ('is_verified', 'active_from')


class EntityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityVerification
        fields = '__all__'


class EntityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in Status])


class BusinessClientEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientEntity
        fields = '__all__'
