from rest_framework import serializers
from .models import MakeYourOwnTrip, MakeYourOwnTripPlaces


class MakeYourOwnTripSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = MakeYourOwnTrip
        fields = '__all__'

    def to_representation(self, instance):
        data = super(MakeYourOwnTripSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        return data

    def create(self, validated_data):
        return MakeYourOwnTrip.objects.create(
            product_id=validated_data["product"],
            created_by_id=validated_data["created_by"],
        )

    def update(self, instance, validated_data):
        instance.product_id = validated_data["product"]
        instance.created_by_id = validated_data["created_by"],
        instance.save()


class MakeYourOwnTripPlacesSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    make_your_own_trip = serializers.IntegerField(default=0)
    place = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = MakeYourOwnTripPlaces
        fields = '__all__'

    def to_representation(self, instance):
        data = super(MakeYourOwnTripPlacesSerializer, self).to_representation(instance)
        data['place'] = instance.place_id
        return data

    def create(self, validated_data):
        return MakeYourOwnTripPlaces.objects.create(
            make_your_own_trip_id=validated_data["make_your_own_trip"],
            place_id=validated_data["place"],
        )

    def update(self, instance, validated_data):
        instance.make_your_own_trip_id = validated_data["make_your_own_trip"]
        instance.place_id = validated_data["place"],
        instance.save()

    @staticmethod
    def bulk_create(make_your_own_trip_places):
        all_make_your_own_trip_places = []
        for make_your_own_trip_place in make_your_own_trip_places:
            make_your_own_trip_place_obj = MakeYourOwnTripPlaces(
                make_your_own_trip_id=make_your_own_trip_place['make_your_own_trip'],
                place_id=make_your_own_trip_place['place'],
            )
            all_make_your_own_trip_places.append(make_your_own_trip_place_obj)
        MakeYourOwnTripPlaces.objects.bulk_create(all_make_your_own_trip_places)

    @staticmethod
    def bulk_delete(make_your_own_trip_id, place_ids):
        MakeYourOwnTripPlaces.objects.filter(make_your_own_trip_id=make_your_own_trip_id, place_id__in=place_ids).delete()
