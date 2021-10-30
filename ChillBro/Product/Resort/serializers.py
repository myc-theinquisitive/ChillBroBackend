from rest_framework import serializers
from .models import ResortRoom, ResortAvailableAmenities, ResortAmenities


class ResortAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResortAmenities
        fields = '__all__'

class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class IdIsAvailableSerializer(IdSerializer):
    is_available = serializers.BooleanField(required=True)



class ResortAmenityIsAvailableSerializer(serializers.Serializer):
    ResortAmenity = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)


class ResortAvailableAmenitiesUpdateSerializer(serializers.Serializer):
    add = ResortAmenityIsAvailableSerializer(many=True)
    change = IdIsAvailableSerializer(many=True)
    delete = IdSerializer(many=True)


class ResortAvailableAmenitiesSerializer(serializers.ModelSerializer):
    # To avoid default serializer validation which takes more no of queries trying to get each element
    # Should handle the validation ourselves
    resort_room = serializers.IntegerField()
    resort_amenity = serializers.IntegerField()

    class Meta:
        model = ResortAvailableAmenities
        fields = '__all__'

    def create(self, validated_data):
        return ResortAvailableAmenities.objects.create(
            resort_room_id=validated_data["resort_room"], resort_amenity_id=validated_data["resort_amenity"],
            is_available=validated_data["is_available"])

    def update(self, instance, validated_data):
        instance.resort_room_id = validated_data["resort_room"]
        instance.resort_amenity_id = validated_data["resort_amenity"]
        instance.is_available = validated_data["is_available"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        resort_amenities = []
        for resort_amenity in validated_data:
            new_resort_amenity = ResortAvailableAmenities(
                resort_room_id=resort_amenity["resort_room"], resort_amenity_id=resort_amenity["resort_amenity"],
                is_available=resort_amenity["is_available"]
            )
            resort_amenities.append(new_resort_amenity)
        ResortAvailableAmenities.objects.bulk_create(resort_amenities)

    @staticmethod
    def bulk_update(validated_data):
        resort_amenities = []
        for resort_amenity in validated_data:
            update_resort_amenity = ResortAvailableAmenities(
                id=resort_amenity["id"], is_available=resort_amenity["is_available"]
            )
            resort_amenities.append(update_resort_amenity)
        ResortAvailableAmenities.objects.bulk_update(resort_amenities, ['is_available'])

    @staticmethod
    def bulk_delete(validated_data):
        resort_available_resort_amenity_ids = []
        for resort_amenity in validated_data:
            resort_available_resort_amenity_ids.append(resort_amenity["id"])
        ResortAvailableAmenities.objects.filter(id__in=resort_available_resort_amenity_ids).delete()


class ResortRoomSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = ResortRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super(ResortRoomSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return ResortRoom.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
