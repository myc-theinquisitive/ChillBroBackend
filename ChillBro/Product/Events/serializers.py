from rest_framework import serializers
from .models import Events, EventSlots, EventPriceClasses
import json


class EventSlotsSerializer(serializers.ModelSerializer):
    event = serializers.IntegerField(default=-1)  # Internal field - avoid validation

    class Meta:
        model = EventSlots
        fields = '__all__'

    def create(self, validated_data):
        return EventSlots.objects.create(
            event_id=validated_data["event"],
            name=validated_data["name"],
            day_start_time=validated_data["day_start_time"],
            day_end_time=validated_data["day_end_time"]
        )

    def update(self, instance, validated_data):
        instance.event_id = validated_data["event"]
        instance.name = validated_data["name"],
        instance.day_start_time = validated_data["day_start_time"],
        instance.day_end_time = validated_data["day_end_time"]
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        event_slots = []
        for slot in validated_data:
            new_slot = EventSlots(
                event_id=slot["event"], name=slot["name"],
                day_start_time=slot["day_start_time"],
                day_end_time=slot["day_end_time"]
            )
            event_slots.append(new_slot)
        EventSlots.objects.bulk_create(event_slots)

    @staticmethod
    def bulk_update(validated_data):
        event_slots = []
        for slot in validated_data:
            update_slot = EventSlots(
                id=slot["id"],
                day_start_time=slot["day_start_time"],
                day_end_time=slot["day_end_time"]
            )
            event_slots.append(update_slot)
        EventSlots.objects.bulk_update(event_slots, ['day_start_time', 'day_end_time'])

    @staticmethod
    def bulk_delete(validated_data):
        event_slot_ids = []
        for slot in validated_data:
            event_slot_ids.append(slot["id"])
        EventSlots.objects.filter(id__in=event_slot_ids).delete()


class EventPriceClassesSerializer(serializers.ModelSerializer):
    event = serializers.IntegerField(default=-1)  # Internal field - avoid validation

    class Meta:
        model = EventPriceClasses
        fields = '__all__'

    def create(self, validated_data):
        return EventPriceClasses.objects.create(
            event_id=validated_data["event"],
            name=validated_data["name"],
            price=validated_data["price"]
        )

    def update(self, instance, validated_data):
        instance.event_id = validated_data["event"]
        instance.name = validated_data["name"],
        instance.price = validated_data["price"],
        instance.save()

    @staticmethod
    def bulk_create(validated_data):
        event_price_classes = []
        for price_class in validated_data:
            new_price_class = EventPriceClasses(
                event_id=price_class["event"], name=price_class["name"],
                price=price_class["price"]
            )
            event_price_classes.append(new_price_class)
        EventPriceClasses.objects.bulk_create(event_price_classes)

    @staticmethod
    def bulk_update(validated_data):
        event_price_classes = []
        for price_class in validated_data:
            update_price_class = EventPriceClasses(
                id=price_class["id"],
                price=validated_data["price"]
            )
            event_price_classes.append(update_price_class)
        EventPriceClasses.objects.bulk_update(event_price_classes, ['price'])

    @staticmethod
    def bulk_delete(validated_data):
        event_price_class_ids = []
        for price_class in validated_data:
            event_price_class_ids.append(price_class["id"])
        EventPriceClasses.objects.filter(id__in=event_price_class_ids).delete()


class EventSerializer(serializers.ModelSerializer):
    # overriding to avoid checks
    product = serializers.CharField(default="", allow_null=True, allow_blank=True)
    tags = serializers.JSONField()

    class Meta:
        model = Events
        fields = '__all__'

    def to_representation(self, instance):
        data = super(EventSerializer, self).to_representation(instance)
        data['product'] = instance.product_id
        data['tags'] = json.loads(instance.tags)
        return data

    def create(self, validated_data):
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        return Events.objects.create(
            product_id=validated_data["product"],
            mode=validated_data["mode"],
            host_app=validated_data["host_app"],
            url_link=validated_data["url_link"],
            payment_type=validated_data["payment_type"],
            has_slots=validated_data["has_slots"],
            start_time=validated_data["start_time"],
            end_time=validated_data["end_time"],
            tags=validated_data["tags"]
        )

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            validated_data["tags"] = json.dumps(validated_data["tags"])

        instance.product_id = validated_data["product"]
        instance.mode = validated_data["mode"]
        instance.host_app = validated_data["host_app"]
        instance.url_link = validated_data["url_link"]
        instance.payment_type = validated_data["payment_type"]
        instance.has_slots = validated_data["has_slots"]
        instance.start_time = validated_data["start_time"]
        instance.end_time = validated_data["end_time"]
        instance.tags = validated_data["tags"]
        instance.save()


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class EventSlotAddSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    day_start_time = serializers.TimeField(required=True)
    day_end_time = serializers.TimeField(required=True)


class EventSlotUpdateExistingSerializer(IdSerializer):
    day_start_time = serializers.TimeField(required=True)
    day_end_time = serializers.TimeField(required=True)


class EventSlotUpdateSerializer(serializers.Serializer):
    add = EventSlotAddSerializer(many=True)
    change = EventSlotUpdateExistingSerializer(many=True)
    delete = IdSerializer(many=True)


class EventPriceClassesAddSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=20)


class EventPriceClassesUpdateExistingSerializer(IdSerializer):
    price = serializers.DecimalField(decimal_places=2, max_digits=20)


class EventPriceClassesUpdateSerializer(serializers.Serializer):
    add = EventPriceClassesAddSerializer(many=True)
    change = EventPriceClassesUpdateExistingSerializer(many=True)
    delete = IdSerializer(many=True)
