from rest_framework import serializers
from .models import HireAVehicle


class HireAVehicleSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = HireAVehicle
        fields = '__all__'

    def to_representation(self, instance):
        data = super(HireAVehicleSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return HireAVehicle.objects.create(
            product_id=validated_data["product"], vehicle_type_id=validated_data["vehicle_type"],
            registration_no=validated_data["registration_no"], default_driver=validated_data["default_driver"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_type_id = validated_data["vehicle_type"],
        instance.registration_no = validated_data["registration_no"]
        instance.default_driver = validated_data["default_driver"]
        instance.save()
