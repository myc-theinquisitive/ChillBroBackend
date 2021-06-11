from rest_framework import serializers
from .models import TravelPackageVehicle


class TravelPackageVehicleSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    vehicle = serializers.CharField(max_length=36)
    travel_package = serializers.CharField(max_length=36)

    class Meta:
        model = TravelPackageVehicle
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TravelPackageVehicleSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['vehicle'] = instance.vehicle_id
        data['travel_package'] = instance.travel_package_id
        return data

    def create(self, validated_data):
        return TravelPackageVehicle.objects.create(
            product_id=validated_data["product"], vehicle_id=validated_data["vehicle"],
            travel_package_id=validated_data["travel_package"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_id = validated_data["vehicle"],
        instance.travel_package_id = validated_data["travel_package"]
        instance.save()
