from rest_framework import serializers
from .models import Place, PlaceImage, get_id


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'

    def create(self, validated_data):
        if "id" not in validated_data:
            validated_data["id"] = get_id()
        return Place.objects.create(id=validated_data["id"], name=validated_data["name"],
                                    description=validated_data["description"], category_id=validated_data["category"],
                                    address_id=validated_data["address_id"])

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.description = validated_data["description"]
        instance.category_id = validated_data["category"]
        instance.address_id = validated_data["address_id"]
        instance.save()


class PlaceImageSerializer(serializers.Serializer):
    place = serializers.CharField(max_length=36, allow_null=True, allow_blank=True)
    image = serializers.ImageField()
    order = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return PlaceImage.objects.create(place_id=validated_data["place"],
                                         image=validated_data["image"], order=validated_data["order"])

    @staticmethod
    def bulk_create(place_images):
        all_images = []
        for image in place_images:
            each_image = PlaceImage(
                place_id=image['place'],
                image=image['image'],
                order=image['order']
            )
            all_images.append(each_image)
        PlaceImage.objects.bulk_create(all_images)


class LocationFilter(serializers.Serializer):
    applied = serializers.BooleanField(default=False)
    city = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)


class GetPlacesBySearchFilters(serializers.Serializer):
    search_text = serializers.CharField(allow_null=True, allow_blank=True)
    sort_filter = serializers.CharField(allow_null=True, allow_blank=True)
    location_filter = LocationFilter()
