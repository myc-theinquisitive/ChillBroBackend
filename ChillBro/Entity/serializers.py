from rest_framework import serializers
from .models import *


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = '__all__'
        read_only_fields = ('activation_status', 'active_from')


class EntityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityVerification
        fields = '__all__'


class EntityVerificationUpdateInputSerializer(serializers.ModelSerializer):
    comments = serializers.CharField()

    class Meta:
        model = MyEntity
        fields = ('activation_status', 'comments', )


class EntityEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        exclude = ('address_id', 'account', 'upi', )


class EntityAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityAccount
        fields = '__all__'


class EntityUPISerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityUPI
        fields = '__all__'


class EntityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in Status])


class BusinessClientEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientEntity
        fields = '__all__'


class EntityDetailsSerializer(EntitySerializer):
    account = EntityAccountSerializer()
    upi = EntityUPISerializer()
