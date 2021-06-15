from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = Vehicle
        fields = '__all__'

    def to_representation(self, instance):
        data = super(VehicleSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):

        return Vehicle.objects.create(
            product_id=validated_data["product"], vehicle_type_id=validated_data["vehicle_type"],
            registration_no=validated_data["registration_no"],registration_type=validated_data['registration_type'])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_type_id = validated_data["vehicle_type"],
        instance.registration_no = validated_data["registration_no"]
        instance.registration_type = validated_data["registration_type"]
        instance.save()
