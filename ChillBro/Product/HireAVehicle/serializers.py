from rest_framework import serializers
from .models import HireAVehicle


class HireAVehicleSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    vehicle = serializers.CharField(max_length=36)
    default_driver = serializers.CharField(max_length=36)

    class Meta:
        model = HireAVehicle
        fields = '__all__'

    def to_representation(self, instance):
        data = super(HireAVehicleSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['vehicle'] = instance.vehicle_id
        data['default_driver'] = instance.default_driver_id
        return data

    def create(self, validated_data):
        return HireAVehicle.objects.create(
            product_id=validated_data["product"], vehicle_id=validated_data["vehicle"],
            default_driver_id=validated_data["default_driver"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_id = validated_data["vehicle"],
        instance.default_driver_id = validated_data["default_driver"]
        instance.save()
