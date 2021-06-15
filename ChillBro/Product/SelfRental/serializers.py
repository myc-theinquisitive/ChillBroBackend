from rest_framework import serializers
from .models import SelfRental, DistancePrice


class SelfRentalSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    vehicle = serializers.CharField(max_length=36)

    class Meta:
        model = SelfRental
        fields = '__all__'

    def to_representation(self, instance):
        data = super(SelfRentalSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['vehicle'] = instance.vehicle_id
        data['excess_price_per_hour'] = instance.excess_price_per_hour
        return data

    def create(self, validated_data):
        return SelfRental.objects.create(
            product_id=validated_data["product"], vehicle_id=validated_data["vehicle"],
            excess_price_per_hour=validated_data['excess_price_per_hour'])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.vehicle_id = validated_data["vehicle"]
        instance.excess_price_per_hour = validated_data["excess_price_per_hour"]
        instance.save()


class DistancePriceSerializer(serializers.ModelSerializer):
    # overriding validation
    self_rental = serializers.CharField(max_length=36, default="")

    class Meta:
        model = DistancePrice
        fields = '__all__'

    def create(self, validated_data):
        return DistancePrice.objects.create(
            self_rental=validated_data["self_rental"],
            price=validated_data["price"],
            km_limit=validated_data["km_limit"],
            excess_price=validated_data["excess_price"],
            is_infinity=validated_data["is_infinity"],
        )

    def update(self, instance, validated_data):
        instance.self_rental_id = validated_data["self_rental"]
        instance.excess_price = validated_data["excess_price"]
        instance.price = validated_data["price"]
        instance.km_limit = validated_data["km_limit"]
        instance.is_infinity = validated_data['is_infinity']
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        print(validated_data, 'validated data')
        distance_prices = []
        for distance_price in validated_data:
            distance_price_object = DistancePrice(
                self_rental=distance_price["self_rental"],
                price=distance_price["price"],
                km_limit=distance_price["km_limit"],
                excess_price=distance_price["excess_price"],
                is_infinity=distance_price["is_infinity"]
            )
            distance_prices.append(distance_price_object)
        DistancePrice.objects.bulk_create(distance_prices)

    @staticmethod
    def bulk_update(validated_data):
        distance_prices = []
        for distance_price in validated_data:
            vehicle_type_characteristic = DistancePrice(
                id=distance_price["id"], price=distance_price["price"],
                excess_price=distance_price["excess_price"],
            )
            distance_prices.append(vehicle_type_characteristic)
        DistancePrice.objects.bulk_update(distance_prices, ['price', 'excess_price', 'excess_price_per_hour'])

    @staticmethod
    def bulk_delete(distance_price_data):
        distance_prices = []
        for distance_price in distance_price_data:
            distance_prices.append(distance_price["id"])
        DistancePrice.objects.filter(id__in=distance_prices).delete()
