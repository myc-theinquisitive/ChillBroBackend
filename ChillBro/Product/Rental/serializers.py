from rest_framework import serializers
from .models import RentalProduct


class RentalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalProduct
        fields = '__all__'

    def create(self, validated_data):
        return RentalProduct.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
