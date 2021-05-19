from rest_framework import serializers
from .models import *
from django.conf import settings


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = '__all__'
        read_only_fields = ('activation_status', 'active_from')
        
    def to_representation(self, data):
        data = super(EntitySerializer, self).to_representation(data)
        data['pan_image'] = data.get('pan_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['registration_image'] = data.get('registration_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['gst_image'] = data.get('gst_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['aadhar_image'] = data.get('aadhar_image').replace(settings.IMAGE_REPLACED_STRING, '')
        return data


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
