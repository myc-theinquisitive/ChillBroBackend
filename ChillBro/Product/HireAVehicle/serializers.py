from rest_framework import serializers
from .models import HireAVehicle, HireAVehicleDistancePrice, HireAVehicleDurationDetails


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

    def create(self, validated_data):
        return HireAVehicleDistancePrice.objects.create(
            hour_price = validated_data["hour_price"], day_price = validated_data["day_price"],\
            excess_km_price=validated_data["excess_km_price"], is_km_infinity=validated_data["is_km_infinity"],\
            km_hour_limit=validated_data["km_hour_limit"], km_day_limit=validated_data["km_day_limit"],\
            excess_hour_duration_price=validated_data["excess_hour_duration_price"], \
            excess_day_duration_price=validated_data["excess_day_duration_price"], \
            single_trip_return_value_per_km=validated_data["single_trip_return_value_per_km"],\
            hire_a_vehicle=validated_data["hire_a_vehicle"])


class HireAVehicleDurationDetailsSerializer(serializers.ModelSerializer):
    # overriding validation
    hire_a_vehicle = serializers.CharField(max_length=36, default="")

    class Meta:
        model = HireAVehicleDurationDetails
        fields = '__all__'

    def to_representation(self, instance):
        data = super(HireAVehicleDurationDetailsSerializer, self).to_representation(instance)
        data['hire_a_vehicle'] = instance.hire_a_vehicle_id
        return data

    def create(self, validated_data):
        return HireAVehicleDurationDetails.objects.create(
            min_hour_duration=validated_data["min_hour_duration"],max_hour_duration=validated_data["max_hour_duration"],\
            min_day_duration=validated_data["min_day_duration"],max_day_duration=validated_data["max_day_duration"],\
            hire_a_vehicle=validated_data["hire_a_vehicle"])
