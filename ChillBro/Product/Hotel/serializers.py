from rest_framework import serializers
from .models import Amenities, HotelAvailableAmenities, HotelRoom


class AmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenities
        fields = '__all__'


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class IdIsAvailableSerializer(IdSerializer):
    is_available = serializers.BooleanField(required=True)


class AmenityIsAvailableSerializer(serializers.Serializer):
    amenity = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)


class HotelAvailableAmenitiesUpdateSerializer(serializers.Serializer):
    add = AmenityIsAvailableSerializer(many=True)
    change = IdIsAvailableSerializer(many=True)
    delete = IdSerializer(many=True)


class HotelAvailableAmenitiesSerializer(serializers.ModelSerializer):
    # To avoid default serializer validation which takes more no of queries trying to get each element
    # Should handle the validation ourselves
    hotel_room = serializers.IntegerField()
    amenity = serializers.IntegerField()

    class Meta:
        model = HotelAvailableAmenities
        fields = '__all__'

    def create(self, validated_data):
        return HotelAvailableAmenities.objects.create(
            hotel_id=validated_data["hotel"], amenity_id=validated_data["amenity"],
            is_available=validated_data["is_available"])

    def update(self, instance, validated_data):
        instance.hotel_room_id = validated_data["hotel_room"]
        instance.amenity_id = validated_data["amenity"]
        instance.is_available = validated_data["is_available"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        hotel_amenities = []
        for amenity in validated_data:
            new_amenity = HotelAvailableAmenities(
                hotel_room_id=amenity["hotel_room"], amenity_id=amenity["amenity"],
                is_available=amenity["is_available"]
            )
            hotel_amenities.append(new_amenity)
        HotelAvailableAmenities.objects.bulk_create(hotel_amenities)

    @staticmethod
    def bulk_update(validated_data):
        hotel_amenities = []
        for amenity in validated_data:
            update_amenity = HotelAvailableAmenities(
                id=amenity["id"], is_available=amenity["is_available"]
            )
            hotel_amenities.append(update_amenity)
        HotelAvailableAmenities.objects.bulk_update(hotel_amenities, ['is_available'])

    @staticmethod
    def bulk_delete(validated_data):
        hotel_available_amenity_ids = []
        for amenity in validated_data:
            hotel_available_amenity_ids.append(amenity["id"])
        HotelAvailableAmenities.objects.filter(id__in=hotel_available_amenity_ids).delete()


class HotelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelRoom
        fields = '__all__'

    def create(self, validated_data):
        return HotelRoom.objects.create(product_id=validated_data["product"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.save()
