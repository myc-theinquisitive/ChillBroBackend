from rest_framework import serializers
from .models import HireAVehicle, HireAVehicleDistancePrice


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


class HireAVehicleDistancePriceSerializer(serializers.ModelSerializer):
    # overriding validation
    hire_a_vehicle = serializers.CharField(max_length=36, default="")

    class Meta:
        model = HireAVehicleDistancePrice
        fields = '__all__'

    def to_representation(self, instance):
        data = super(HireAVehicleDistancePriceSerializer, self).to_representation(instance)
        data['hire_a_vehicle'] = instance.hire_a_vehicle_id
        return data

    def bulk_create(self, validated_data):
        print(validated_data,"validated data")
        distance_prices = []
        for distance_price in validated_data:
            distance_price_object = HireAVehicleDistancePrice(
                hire_a_vehicle=distance_price["hire_a_vehicle"],
                duration_type=distance_price["duration_type"],
                km_limit=distance_price["km_limit"],
                km_price=distance_price["km_price"],
                excess_km_price=distance_price["excess_km_price"],
                excess_duration_price = distance_price["excess_duration_price"],
                is_infinity=distance_price["is_infinity"],
                single_trip_return_value_per_km=distance_price["single_trip_return_value_per_km"],
                min_time_duration=distance_price["min_time_duration"],
                max_time_duration=distance_price["max_time_duration"]
            )
            distance_prices.append(distance_price_object)
        print(distance_prices,"distance prices")
        some = HireAVehicleDistancePrice.objects.bulk_create(distance_prices)
        print(some,"final")