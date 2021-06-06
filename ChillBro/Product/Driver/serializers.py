from rest_framework import serializers
from .models import Driver


class DriverSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    preferred_vehicle = serializers.CharField(max_length=36)

    class Meta:
        model = Driver
        fields = '__all__'

    def to_representation(self, instance):
        data = super(DriverSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['preferred_vehicle'] = instance.preferred_vehicle_id
        return data

    def create(self, validated_data):
        return Driver.objects.create(
            product_id=validated_data["product"], preferred_vehicle_id=validated_data["preferred_vehicle"],
            address_id=validated_data["address_id"], licensed_from=validated_data["licensed_from"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.preferred_vehicle_id = validated_data["preferred_vehicle"]
        instance.address_id = validated_data["address_id"]
        instance.licensed_from = validated_data["licensed_from"]
        instance.save()
