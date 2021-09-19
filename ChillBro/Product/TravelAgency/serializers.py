from rest_framework import serializers
from .models import TravelCharacteristics, TravelAgencyImage, TravelAgencyPlaces, TravelAgency, get_id, \
    TravelAgencyCharacteristics
import json


class TravelAgencySerializer(serializers.ModelSerializer):
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField(max_length=20))

    class Meta:
        model = TravelAgency
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TravelAgencySerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['tags'] = json.loads(instance.tags)
        return data

    def create(self, validated_data):
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        return TravelAgency.objects.create(
            product_id=validated_data["product"],
            tags=validated_data["tags"],
            duration_in_days=validated_data["duration_in_days"],
            duration_in_nights=validated_data["duration_in_nights"],
            starting_point=validated_data["starting_point"])

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        instance.product_id = validated_data["product"]
        instance.duration_in_days = validated_data["duration_in_days"]
        instance.duration_in_nights = validated_data["duration_in_nights"]
        instance.tags = validated_data["tags"]
        instance.starting_point = validated_data["starting_point"]
        instance.save()


class TravelAgencyPlacesSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    travel_agency = serializers.IntegerField(default=0)
    place = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = TravelAgencyPlaces
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TravelAgencyPlacesSerializer, self).to_representation(instance)
        data['place'] = instance.place_id
        return data

    def create(self, validated_data):
        return TravelAgencyPlaces.objects.create(
            travel_agency_id=validated_data["travel_agency"], place_id=validated_data["place"],
            order=validated_data["order"], type=validated_data["type"],
            day_number=validated_data['day_number']
        )

    def update(self, instance, validated_data):
        instance.travel_agency_id = validated_data["travel_agency"]
        instance.place_id = validated_data["place"],
        instance.order = validated_data["order"]
        instance.type = validated_data["type"]
        instance.day_number = validated_data["day_number"]
        instance.save()

    @staticmethod
    def bulk_create(agency_places):
        all_agency_places = []
        for agency_place in agency_places:
            agency_place_obj = TravelAgencyPlaces(
                travel_agency_id=agency_place['travel_agency'],
                place_id=agency_place['place'],
                type=agency_place['type'],
                order=agency_place['order'],
                day_number=agency_place['day_number']
            )
            all_agency_places.append(agency_place_obj)
        TravelAgencyPlaces.objects.bulk_create(all_agency_places)

    @staticmethod
    def bulk_delete(travel_agency_id, place_ids):
        TravelAgencyPlaces.objects.filter(travel_agency_id=travel_agency_id, place_id__in=place_ids).delete()


class TravelAgencyImageSerializer(serializers.Serializer):
    travel_agency = serializers.CharField(max_length=36, allow_null=True, allow_blank=True)
    image = serializers.ImageField()
    order = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return TravelAgencyImage.objects.create(travel_agency_id=validated_data["travel_agency"],
                                                image=validated_data["image"], order=validated_data["order"])

    @staticmethod
    def bulk_create(travel_agency_images):
        all_images = []
        for image in travel_agency_images:
            each_image = TravelAgencyImage(
                travel_agency=image['travel_agency'],
                image=image['image'],
                order=image['order']
            )
            all_images.append(each_image)
        TravelAgencyImage.objects.bulk_create(all_images)


class TravelCharacteristicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelCharacteristics
        fields = "__all__"


class TravelAgencyCharacteristicsSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    travel_agency = serializers.IntegerField(default=0)

    class Meta:
        model = TravelAgencyCharacteristics
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TravelAgencyCharacteristicsSerializer, self).to_representation(instance)
        data['travel_agency'] = instance.travel_agency_id
        return data

    def create(self, validated_data):
        return TravelAgencyCharacteristics.objects.create(
            travel_agency_id=validated_data["travel_agency"],
            travel_characteristics_id=validated_data["travel_characteristics"],
        )

    def update(self, instance, validated_data):
        instance.travel_agency_id = validated_data["travel_agency"]
        instance.travel_characteristics_id = validated_data["travel_characteristics"],
        instance.save()

    @staticmethod
    def bulk_create(agency_characteristics):
        all_agency_characteristics = []
        for agency_characteristic in agency_characteristics:
            agency_characteristic_obj = TravelAgencyCharacteristics(
                travel_agency_id=agency_characteristic['travel_agency'],
                travel_characteristics_id=agency_characteristic['travel_characteristics'],
            )
            all_agency_characteristics.append(agency_characteristic_obj)
        TravelAgencyCharacteristics.objects.bulk_create(all_agency_characteristics)

    @staticmethod
    def bulk_delete(travel_agency_id, characteristics_ids):
        TravelAgencyCharacteristics.objects.filter(travel_agency_id=travel_agency_id,
                                                   travel_characteristics_id__in=characteristics_ids).delete()
