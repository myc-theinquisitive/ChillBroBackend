from rest_framework import serializers
from .models import Place, PlaceImage


class PlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'

    def create(self, validated_data):
        return Place.objects.create(name=validated_data["name"], description=validated_data["description"],
                                    category_id=validated_data["category"], address_id=validated_data["address_id"])

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
