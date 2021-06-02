from rest_framework import serializers
from .models import VehicleType, VehicleCharacteristics, VehicleTypeCharacteristics, get_id


class VehicleCharacteristicsSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleCharacteristics
        fields = '__all__'


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class IdValueSerializer(IdSerializer):
    value = serializers.CharField(max_length=30)


class CharacteristicValueSerializer(serializers.Serializer):
    vehicle_characteristic = serializers.IntegerField(required=True)
    value = serializers.CharField(max_length=30)


class VehicleTypeCharacteristicsUpdateSerializer(serializers.Serializer):
    add = CharacteristicValueSerializer(many=True)
    change = IdValueSerializer(many=True)
    delete = IdSerializer(many=True)


class VehicleTypeCharacteristicsSerializer(serializers.ModelSerializer):
    # overriding validation
    vehicle_type = serializers.CharField(max_length=36, default="")
    vehicle_characteristic = serializers.IntegerField()

    class Meta:
        model = VehicleTypeCharacteristics
        fields = '__all__'

    def create(self, validated_data):
        return VehicleTypeCharacteristics.objects.create(
            vehicle_type_id=validated_data["vehicle_type"],
            vehicle_characteristic_id=validated_data["vehicle_characteristic"],
            value=validated_data["value"])

    def update(self, instance, validated_data):
        instance.vehicle_type_id = validated_data["vehicle_type"]
        instance.vehicle_characteristic_id = validated_data["vehicle_characteristic"]
        instance.value = validated_data["value"]
        instance.save()

    @staticmethod
    def bulk_create(vehicle_type_characteristics_data):
        vehicle_type_characteristics = []
        for vehicle_type_characteristic_data in vehicle_type_characteristics_data:
            vehicle_type_characteristic = VehicleTypeCharacteristics(
                vehicle_type_id=vehicle_type_characteristic_data["vehicle_type"],
                vehicle_characteristic_id=vehicle_type_characteristic_data["vehicle_characteristic"],
                value=vehicle_type_characteristic_data["value"]
            )
            vehicle_type_characteristics.append(vehicle_type_characteristic)
        VehicleTypeCharacteristics.objects.bulk_create(vehicle_type_characteristics)

    @staticmethod
    def bulk_update(vehicle_type_characteristics_data):
        vehicle_type_characteristics = []
        for vehicle_type_characteristic_data in vehicle_type_characteristics_data:
            vehicle_type_characteristic = VehicleTypeCharacteristics(
                id=vehicle_type_characteristic_data["id"], value=vehicle_type_characteristic_data["value"]
            )
            vehicle_type_characteristics.append(vehicle_type_characteristic)
        VehicleTypeCharacteristics.objects.bulk_update(vehicle_type_characteristics, ['value'])

    @staticmethod
    def bulk_delete(vehicle_type_characteristics_data):
        vehicle_type_characteristic_ids = []
        for vehicle_type_characteristic_data in vehicle_type_characteristics_data:
            vehicle_type_characteristic_ids.append(vehicle_type_characteristic_data["id"])
        VehicleTypeCharacteristics.objects.filter(id__in=vehicle_type_characteristic_ids).delete()


class VehicleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleType
        fields = '__all__'

    def create(self, validated_data):
        if "id" not in validated_data:
            validated_data["id"] = get_id()
        return VehicleType.objects.create(
            id=validated_data["id"], name=validated_data["name"],
            description=validated_data["description"], no_of_people=validated_data["no_of_people"],
            category_id=validated_data["category"], category_product_id=validated_data["category_product"],
            wheel_type=validated_data["wheel_type"], image=validated_data["image"])

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.description = validated_data["description"]

        # TODO: Temporarily disabling as data got is in tuple format from postman using forms
        # instance.no_of_people = validated_data["no_of_people"],
        # instance.category_id = validated_data["category"]
        # instance.category_product_id = validated_data["category_product"],

        instance.wheel_type = validated_data["wheel_type"]
        instance.image = validated_data["image"]
        instance.save()
