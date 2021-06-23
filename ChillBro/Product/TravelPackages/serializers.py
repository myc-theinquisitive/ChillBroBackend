from rest_framework import serializers
from .models import TravelPackage, PackagePlaces, TravelPackageImage, get_id
import json


class TravelPackageSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(max_length=20))

    class Meta:
        model = TravelPackage
        fields = '__all__'

    def to_representation(self, instance):
        data = super(TravelPackageSerializer, self).to_representation(instance)
        data['tags'] = json.loads(instance.tags)
        return data

    def create(self, validated_data):
        if "id" not in validated_data:
            validated_data["id"] = get_id()
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        return TravelPackage.objects.create(
            id=validated_data["id"], name=validated_data["name"], description=validated_data["description"],
            category_id=validated_data["category"], tags=validated_data["tags"],
            category_product_id=validated_data["category_product"],
            duration_in_days=validated_data["duration_in_days"],
            duration_in_nights=validated_data["duration_in_nights"])

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.category_id = validated_data["category"]
        instance.category_product_id = validated_data["category_product"]
        instance.duration_in_days = validated_data["duration_in_days"]
        instance.duration_in_nights = validated_data["duration_in_nights"]
        instance.tags = validated_data["tags"]
        instance.save()


class PackagePlacesSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    travel_package = serializers.IntegerField(default=0)
    place = serializers.CharField(default="", allow_null=True, allow_blank=True)

    class Meta:
        model = PackagePlaces
        fields = '__all__'

    def to_representation(self, instance):
        data = super(PackagePlacesSerializer, self).to_representation(instance)
        data['place'] = instance.place_id
        return data

    def create(self, validated_data):
        return PackagePlaces.objects.create(
            travel_package_id=validated_data["travel_package"], place_id=validated_data["place"],
            order=validated_data["order"], in_return=validated_data["in_return"],
            duration_to_reach=validated_data["duration_to_reach"], spending_time=validated_data["spending_time"]
        )

    def update(self, instance, validated_data):
        instance.travel_package_id = validated_data["travel_package"]
        instance.place_id = validated_data["place"],
        instance.order = validated_data["order"]
        instance.in_return = validated_data["in_return"]
        instance.duration_to_reach = validated_data["duration_to_reach"]
        instance.spending_time = validated_data["spending_time"]
        instance.save()

    @staticmethod
    def bulk_create(package_places):
        all_package_places = []
        for package_place in package_places:
            package_place_obj = PackagePlaces(
                travel_package_id=package_place['travel_package'],
                place_id=package_place['place'],
                in_return=package_place['in_return'],
                order=package_place['order'],
                duration_to_reach=package_place['duration_to_reach'],
                spending_time=package_place['spending_time']
            )
            all_package_places.append(package_place_obj)
        PackagePlaces.objects.bulk_create(all_package_places)

    @staticmethod
    def bulk_delete(travel_package_id, place_ids):
        PackagePlaces.objects.filter(travel_package_id=travel_package_id, place_id__in=place_ids).delete()


class TravelPackageImageSerializer(serializers.Serializer):
    travel_package = serializers.CharField(max_length=36, allow_null=True, allow_blank=True)
    image = serializers.ImageField()
    order = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return TravelPackageImage.objects.create(travel_package_id=validated_data["travel_package"],
                                                 image=validated_data["image"], order=validated_data["order"])

    @staticmethod
    def bulk_create(travel_package_images):
        all_images = []
        for image in travel_package_images:
            each_image = TravelPackageImage(
                travel_package=image['travel_package'],
                image=image['image'],
                order=image['order']
            )
            all_images.append(each_image)
        TravelPackageImage.objects.bulk_create(all_images)
