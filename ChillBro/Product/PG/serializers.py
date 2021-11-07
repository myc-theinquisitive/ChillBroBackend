from rest_framework import serializers
from .models import PGRoom, PGAvailableAmenities, PGAmenities


class PGAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PGAmenities
        fields = '__all__'

class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class IdIsAvailableSerializer(IdSerializer):
    is_available = serializers.BooleanField(required=True)



class PGAmenityIsAvailableSerializer(serializers.Serializer):
    PGAmenity = serializers.IntegerField(required=True)
    is_available = serializers.BooleanField(required=True)


class PGAvailableAmenitiesUpdateSerializer(serializers.Serializer):
    add = PGAmenityIsAvailableSerializer(many=True)
    change = IdIsAvailableSerializer(many=True)
    delete = IdSerializer(many=True)


class PGAvailableAmenitiesSerializer(serializers.ModelSerializer):
    # To avoid default serializer validation which takes more no of queries trying to get each element
    # Should handle the validation ourselves
    pg_room = serializers.IntegerField()
    pg_amenity = serializers.IntegerField()

    class Meta:
        model = PGAvailableAmenities
        fields = '__all__'

    def create(self, validated_data):
        return PGAvailableAmenities.objects.create(
            pg_room_id=validated_data["pg_room"], pg_amenity_id=validated_data["pg_amenity"],
            is_available=validated_data["is_available"])

    def update(self, instance, validated_data):
        instance.pg_room_id = validated_data["pg_room"]
        instance.pg_amenity_id = validated_data["pg_amenity"]
        instance.is_available = validated_data["is_available"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        pg_amenities = []
        for pg_amenity in validated_data:
            new_pg_amenity = PGAvailableAmenities(
                pg_room_id=pg_amenity["pg_room"], pg_amenity_id=pg_amenity["pg_amenity"],
                is_available=pg_amenity["is_available"]
            )
            pg_amenities.append(new_pg_amenity)
        PGAvailableAmenities.objects.bulk_create(pg_amenities)

    @staticmethod
    def bulk_update(validated_data):
        pg_amenities = []
        for pg_amenity in validated_data:
            update_pg_amenity = PGAvailableAmenities(
                id=pg_amenity["id"], is_available=pg_amenity["is_available"]
            )
            pg_amenities.append(update_pg_amenity)
        PGAvailableAmenities.objects.bulk_update(pg_amenities, ['is_available'])

    @staticmethod
    def bulk_delete(validated_data):
        pg_available_pg_amenity_ids = []
        for pg_amenity in validated_data:
            pg_available_pg_amenity_ids.append(pg_amenity["id"])
        PGAvailableAmenities.objects.filter(id__in=pg_available_pg_amenity_ids).delete()


class PGRoomSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = PGRoom
        fields = '__all__'

    def to_representation(self, instance):
        data = super(PGRoomSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return PGRoom.objects.create(product_id=validated_data["product"],
                                     no_of_sharing=validated_data["no_of_sharing"])

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.no_of_sharing = validated_data["no_of_sharing"]
        instance.save()
