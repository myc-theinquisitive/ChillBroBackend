from rest_framework import serializers
from .models import *
from django.conf import settings


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


class EntityAvailableAmenitiesUpdateSerializer(serializers.Serializer):
    add = AmenityIsAvailableSerializer(many=True, allow_null=True)
    change = IdIsAvailableSerializer(many=True, allow_null=True)
    delete = IdSerializer(many=True, allow_null=True)


class EntityAvailableAmenitiesSerializer(serializers.ModelSerializer):
    entity = serializers.CharField(max_length=36, allow_null=True, allow_blank=True)
    amenity = serializers.IntegerField()

    class Meta:
        model = EntityAvailableAmenities
        fields = '__all__'

    def create(self, validated_data):
        return EntityAvailableAmenities.objects.create(
            entity_id=validated_data["entity"], amenity_id=validated_data["amenity"],
            is_available=validated_data["is_available"])

    def update(self, instance, validated_data):
        instance.entity_id = validated_data["entity"]
        instance.amenity_id = validated_data["amenity"]
        instance.is_available = validated_data["is_available"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        entity_amenities = []
        for amenity in validated_data:
            new_amenity = EntityAvailableAmenities(
                entity_id=amenity["entity"], amenity_id=amenity["amenity"],
                is_available=amenity["is_available"]
            )
            entity_amenities.append(new_amenity)
        EntityAvailableAmenities.objects.bulk_create(entity_amenities)

    @staticmethod
    def bulk_update(validated_data):
        entity_amenities = []
        for amenity in validated_data:
            update_amenity = EntityAvailableAmenities(
                id=amenity["id"], is_available=amenity["is_available"]
            )
            entity_amenities.append(update_amenity)
        EntityAvailableAmenities.objects.bulk_update(entity_amenities, ['is_available'])

    @staticmethod
    def bulk_delete(validated_data):
        entity_available_amenity_ids = []
        for amenity in validated_data:
            entity_available_amenity_ids.append(amenity["id"])
        EntityAvailableAmenities.objects.filter(id__in=entity_available_amenity_ids).delete()


class NewEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        exclude = ('registration', 'account', 'upi', 'address_id')
        read_only_fields = ('activation_status', 'active_from')


class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        fields = '__all__'
        read_only_fields = ('activation_status', 'active_from')

    def create(self, validated_data):
        if "id" not in validated_data:
            validated_data["id"] = get_id()
        return MyEntity.objects.create(
            id=validated_data["id"], name=validated_data["name"], type=validated_data["type"],
            sub_type=validated_data["sub_type"], address_id=validated_data["address_id"],
            registration_id=validated_data["registration"],
            account_id=validated_data["account"], upi_id=validated_data["upi"],
            description=validated_data["description"]
        )


class EntityImageSerializer(serializers.Serializer):
    entity = serializers.CharField(max_length=36, allow_null=True, allow_blank=True)
    image = serializers.ImageField()
    order = serializers.IntegerField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        return EntityImage.objects.create(entity_id=validated_data["entity"],
                                          image=validated_data["image"], order=validated_data["order"])

    @staticmethod
    def bulk_create(entity_images):
        all_images = []
        for image in entity_images:
            each_image = EntityImage(
                entity=image['entity'],
                image=image['image'],
                order=image['order']
            )
            all_images.append(each_image)
        EntityImage.objects.bulk_create(all_images)


class EntityRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityRegistration
        fields = '__all__'

    def to_representation(self, data):
        data = super(EntityRegistrationSerializer, self).to_representation(data)
        data['pan_image'] = data.get('pan_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['registration_image'] = data.get('registration_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['gst_image'] = data.get('gst_image').replace(settings.IMAGE_REPLACED_STRING, '')
        data['aadhar_image'] = data.get('aadhar_image').replace(settings.IMAGE_REPLACED_STRING, '')
        return data


class EntityVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityVerification
        fields = '__all__'


class EntityVerificationUpdateInputSerializer(serializers.ModelSerializer):
    comments = serializers.CharField()

    class Meta:
        model = MyEntity
        fields = ('activation_status', 'comments', )


class EntityEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyEntity
        exclude = ('address_id', 'account', 'upi', 'registration', )


class EntityAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityAccount
        fields = '__all__'


class EntityUPISerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityUPI
        fields = '__all__'


class EntityStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[(status.name, status.value) for status in Status])


class BusinessClientEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessClientEntity
        fields = '__all__'


class EntityDetailsSerializer(EntitySerializer):
    registration = EntityRegistrationSerializer()
    account = EntityAccountSerializer()
    upi = EntityUPISerializer()


class GetEntitiesByStatusSerializer(serializers.Serializer):
    entity_types = serializers.ListField(
        child=serializers.CharField()
    )
    statuses = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )


class LocationFilter(serializers.Serializer):
    applied = serializers.BooleanField(default=False)
    city = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)


class GetEntitiesBySearchFilters(serializers.Serializer):
    search_text = serializers.CharField(allow_null=True, allow_blank=True)
    sort_filter = serializers.CharField(allow_null=True, allow_blank=True)
    location_filter = LocationFilter()
    trending_type = serializers.CharField(allow_null=True, allow_blank=True)
