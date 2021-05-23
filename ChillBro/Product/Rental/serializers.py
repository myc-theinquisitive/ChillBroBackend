from rest_framework import serializers
from .models import RentalProduct


class RentalProductSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = RentalProduct
        fields = '__all__'

    def create(self, validated_data):
        return RentalProduct.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
