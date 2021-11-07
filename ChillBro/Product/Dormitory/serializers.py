from rest_framework import serializers
from .models import DormitoryRoom, DormitoryAvailableAmenities, DormitoryAmenities


class DormitoryAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DormitoryAmenities
        fields = '__all__'

class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class IdIsAvailableSerializer(IdSerializer):
    is_available = serializers.BooleanField(required=True)



class DormitoryAmenityIsAvailableSerializer(serializers.Serializer):
    DormitoryAmenity = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)


class DormitoryAvailableAmenitiesUpdateSerializer(serializers.Serializer):
    add = DormitoryAmenityIsAvailableSerializer(many=True)
    change = IdIsAvailableSerializer(many=True)
    delete = IdSerializer(many=True)


class DormitoryAvailableAmenitiesSerializer(serializers.ModelSerializer):
    # To avoid default serializer validation which takes more no of queries trying to get each element
    # Should handle the validation ourselves
    dormitory_room = serializers.IntegerField()
    dormitory_amenity = serializers.IntegerField()

    class Meta:
        model = DormitoryAvailableAmenities
        fields = '__all__'

    def create(self, validated_data):
        return DormitoryAvailableAmenities.objects.create(
            dormitory_room_id=validated_data["dormitory_room"], dormitory_amenity_id=validated_data["dormitory_amenity"],
            is_available=validated_data["is_available"])

    def update(self, instance, validated_data):
        instance.dormitory_room_id = validated_data["dormitory_room"]
        instance.dormitory_amenity_id = validated_data["dormitory_amenity"]
        instance.is_available = validated_data["is_available"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        dormitory_amenities = []
        for dormitory_amenity in validated_data:
            new_dormitory_amenity = DormitoryAvailableAmenities(
                dormitory_room_id=dormitory_amenity["dormitory_room"], dormitory_amenity_id=dormitory_amenity["dormitory_amenity"],
                is_available=dormitory_amenity["is_available"]
            )
            dormitory_amenities.append(new_dormitory_amenity)
        DormitoryAvailableAmenities.objects.bulk_create(dormitory_amenities)

    @staticmethod
    def bulk_update(validated_data):
        dormitory_amenities = []
        for dormitory_amenity in validated_data:
            update_dormitory_amenity = DormitoryAvailableAmenities(
                id=dormitory_amenity["id"], is_available=dormitory_amenity["is_available"]
            )
            dormitory_amenities.append(update_dormitory_amenity)
        DormitoryAvailableAmenities.objects.bulk_update(dormitory_amenities, ['is_available'])

    @staticmethod
    def bulk_delete(validated_data):
        dormitory_available_dormitory_amenity_ids = []
        for dormitory_amenity in validated_data:
            dormitory_available_dormitory_amenity_ids.append(dormitory_amenity["id"])
        DormitoryAvailableAmenities.objects.filter(id__in=dormitory_available_dormitory_amenity_ids).delete()


class DormitoryRoomSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = DormitoryRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super(DormitoryRoomSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return DormitoryRoom.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
