from rest_framework import serializers
from .models import PaidAmenities


class PaidAmenitiesSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = PaidAmenities
        fields = '__all__'

    def to_representation(self, instance):
        data = super(PaidAmenitiesSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return PaidAmenities.objects.create(
            product_id=validated_data["product"],
        )

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
