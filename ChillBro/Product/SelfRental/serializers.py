from rest_framework import serializers
from .models import SelfRental


class SelfRentalSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(max_length=36)

    class Meta:
        model = SelfRental
        fields = '__all__'

    def to_representation(self, instance):
        data = super(SelfRentalSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return SelfRental.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
