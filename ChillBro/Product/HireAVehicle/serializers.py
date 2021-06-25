from rest_framework import serializers
from .models import HireAVehicle, HireAVehicleDistancePrice, HireAVehicleDurationDetails


class HireAVehicleSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    vehicle = serializers.CharField(max_length=36)
    default_driver = serializers.CharField(max_length=36)
    distance_price = serializers.CharField(default="", allow_null=True, allow_blank=True)
    duration_details = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = HireAVehicle
        fields = '__all__'

    def to_representation(self, instance):
        data = super(HireAVehicleSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['vehicle'] = instance.vehicle_id
        data['default_driver'] = instance.default_driver_id
        data['distance_price'] = instance.distance_price_id
        data['duration_details'] = instance.duration_details
        return data

    def create(self, validated_data):
        return HireAVehicle.objects.create(
            product_id=validated_data["product"], vehicle_id=validated_data["vehicle"],
            default_driver_id=validated_data["default_driver"],distance_price= validated_data['distance_price'],
            duration_details=validated_data["duration_details"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_id = validated_data["vehicle"],
        instance.default_driver_id = validated_data["default_driver"]
        instance.save()


class HireAVehicleDistancePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = HireAVehicleDistancePrice
        fields = '__all__'

    def create(self, validated_data):
        return HireAVehicleDistancePrice.objects.create(
            excess_km_price=validated_data["excess_km_price"], is_km_infinity=validated_data["is_km_infinity"],
            km_hour_limit=validated_data["km_hour_limit"], km_day_limit=validated_data["km_day_limit"],
            single_trip_return_value_per_km=validated_data["single_trip_return_value_per_km"])


class HireAVehicleDurationDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = HireAVehicleDurationDetails
        fields = '__all__'

    def create(self, validated_data):
        return HireAVehicleDurationDetails.objects.create(
            hour_price=validated_data["hour_price"], day_price=validated_data["day_price"],
            excess_hour_duration_price=validated_data["excess_hour_duration_price"],
            excess_day_duration_price=validated_data["excess_day_duration_price"],
            min_hour_duration=validated_data["min_hour_duration"],max_hour_duration=validated_data["max_hour_duration"],
            min_day_duration=validated_data["min_day_duration"],max_day_duration=validated_data["max_day_duration"])
