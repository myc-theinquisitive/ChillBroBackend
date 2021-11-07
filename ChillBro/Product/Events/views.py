from Product.product_interface import ProductInterface
from .serializers import EventSerializer, EventSlotsSerializer, EventPriceClassesSerializer, \
    EventPriceClassesUpdateSerializer, EventSlotUpdateSerializer
from typing import Dict, List
from collections import defaultdict
from .models import Events, EventSlots, EventPriceClasses


def validate_event_slot_ids(event_slot_ids: List[int]) -> (bool, List[int]):
    existing_slot_ids = EventSlots.objects.filter(id__in=event_slot_ids).values_list('id', flat=True)
    if len(existing_slot_ids) != len(event_slot_ids):
        return False, set(event_slot_ids) - set(existing_slot_ids)
    return True, []


def validate_event_price_class_ids(event_price_class_ids: List[int]) -> (bool, List[int]):
    existing_price_class_ids = EventPriceClasses.objects.filter(id__in=event_price_class_ids)\
        .values_list('id', flat=True)
    if len(existing_price_class_ids) != len(event_price_class_ids):
        return False, set(event_price_class_ids) - set(existing_price_class_ids)
    return True, []


class EventView(ProductInterface):

    # define all required instance variables
    def __init__(self):
        self.event_serializer = None
        self.event_object = None

        self.slots_data = None
        self.price_classes_data = None

    # initialize the instance variables before accessing
    def initialize_product_class(self, event_data):
        if event_data:
            self.slots_data = event_data.pop("slots", None)
            self.price_classes_data = event_data.pop("price_classes", None)

        event_object_defined = self.event_object is not None
        event_data_defined = event_data is not None

        # for update
        if event_object_defined and event_data_defined:
            self.event_serializer = EventSerializer(
                self.event_object, data=event_data)
        # for create
        elif event_data_defined:
            self.event_serializer = EventSerializer(data=event_data)
        # for get
        elif event_object_defined:
            self.event_serializer = EventSerializer(self.event_object)
        else:
            self.event_serializer = EventSerializer()

    def validate_create_data(self, event_data: Dict) -> (bool, Dict):
        is_valid = True
        errors = defaultdict(list)

        # Initializing instance variables
        self.initialize_product_class(event_data)

        event_data_valid = self.event_serializer.is_valid()
        if not event_data_valid:
            is_valid = False
            errors.update(self.event_serializer.errors)

        event_slots_serializer = EventSlotsSerializer(data=self.slots_data, many=True)
        event_slots_data_valid = event_slots_serializer.is_valid()

        if not event_slots_data_valid:
            is_valid = False
            errors.update(event_slots_serializer.errors)
            return is_valid, errors

        event_price_classes_serializer = EventPriceClassesSerializer(data=self.price_classes_data, many=True)
        event_price_classes_data_valid = event_price_classes_serializer.is_valid()

        if not event_price_classes_data_valid:
            is_valid = False
            errors.update(event_price_classes_serializer.errors)
            return is_valid, errors

        return is_valid, errors

    def create(self, event_data):
        """
        event: {
            "product_id": string, # internal data need not be validated
            "mode": string,
            "host_app": string,
            "url_link": string,
            "payment_type": string,
            "has_slots": bool,
            "start_time": string,
            "end_time": string,
            "tags": ["DJ", "Private Party"],
            "slots: [
                {
                    "name": string,
                    "day_start_time": string,
                    "day_end_time": string
                }
            ],
            "price_classes": [
                {
                    "name": string,
                    "price": string
                }
            ]
        }
        """

        event_object = self.event_serializer.create(event_data)

        for slots in self.slots_data:
            slots["event"] = event_object.id
        event_slots_serializer = EventSlotsSerializer()
        event_slots_serializer.bulk_create(self.slots_data)

        for price_class in self.price_classes_data:
            price_class["event"] = event_object.id
        event_price_classes_serializer = EventPriceClassesSerializer()
        event_price_classes_serializer.bulk_create(self.price_classes_data)

        return {
            "id": event_object.id
        }

    def validate_update_data(self, event_data):
        is_valid = True
        errors = defaultdict(list)

        # Get the instance of product to be updated
        try:
            self.event_object \
                = Events.objects.get(product_id=event_data["product"])
        except Events.DoesNotExist:
            return False, {"errors": "Event does not Exist!!!"}

        # Initializing instance variables
        self.initialize_product_class(event_data)
        event_data_valid = self.event_serializer.is_valid()
        if not event_data_valid:
            is_valid = False
            errors.update(self.event_serializer.errors)

        event_slots_update_serializer = EventSlotUpdateSerializer(data=self.slots_data)
        event_slots_update_data_valid = event_slots_update_serializer.is_valid()

        if not event_slots_update_data_valid:
            is_valid = False
            errors.update(event_slots_update_serializer.errors)
            return is_valid, errors

        event_price_classes_update_serializer = EventPriceClassesUpdateSerializer(data=self.price_classes_data)
        event_price_classes_update_data_valid = event_price_classes_update_serializer.is_valid()

        if not event_price_classes_update_data_valid:
            is_valid = False
            errors.update(event_price_classes_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        event_slot_ids = []
        for slot in self.slots_data["add"]:
            slot_exists = EventSlots.objects \
                .filter(event=self.event_object, name=slot["name"]).exists()
            if slot_exists:
                is_valid = False
                errors["Event-Slot"].append("Event-{0}, Slot-{1}: Already Exists!"
                                            .format(self.event_object.id, slot["name"]))

            slot["event"] = self.event_object.id

        for slot in self.slots_data["change"]:
            event_slot_ids.append(slot["id"])

        for slot in self.slots_data["delete"]:
            event_slot_ids.append(slot["id"])

        event_slot_ids_valid, invalid_event_slot_ids = validate_event_slot_ids(event_slot_ids)
        if not event_slot_ids_valid:
            is_valid = False
            errors["invalid_event_slot_ids"] = invalid_event_slot_ids

        event_price_class_ids = []
        for price_class in self.price_classes_data["add"]:
            price_class_exists = EventPriceClasses.objects \
                .filter(event=self.event_object, name=price_class["name"]).exists()
            if price_class_exists:
                is_valid = False
                errors["Event-PriceClass"].append("Event-{0}, PriceClass-{1}: Already Exists!"
                                                  .format(self.event_object.id, price_class["name"]))

            price_class["event"] = self.event_object.id

        for price_class in self.price_classes_data["change"]:
            event_price_class_ids.append(price_class["id"])

        for price_class in self.price_classes_data["delete"]:
            event_price_class_ids.append(price_class["id"])

        event_price_class_ids_valid, invalid_event_price_class_ids = validate_event_price_class_ids(
            event_price_class_ids)
        if not event_price_class_ids_valid:
            is_valid = False
            errors["invalid_event_price_class_ids"] = invalid_event_price_class_ids

        return is_valid, errors

    def update(self, event_data):
        """
        event: {
            "product_id": string, # internal data need not be validated
            "mode": string,
            "host_app": string,
            "url_link": string,
            "payment_type": string,
            "has_slots": bool,
            "start_time": string,
            "end_time": string,
            "tags": ["DJ", "Private Party"],
            "slots": {
                "add": [
                    {
                        "name": string,
                        "day_start_time": string,
                        "day_end_time": string
                    }
                ],
                "update": [
                    {
                        "id": int,
                        "day_start_time": string,
                        "day_end_time": string
                    }
                ],
                "delete": [id]
            },
            "price_classes": {
                "add": [
                    {
                        "name": string,
                        "price": string
                    }
                ],
                "update": [
                    {
                        "id": int,
                        "price": string
                    }
                ],
                "delete": [id]
            }
        }
        """

        self.event_serializer.update(self.event_object, event_data)

        event_slots_serializer = EventSlotsSerializer()
        event_slots_serializer.bulk_create(self.slots_data["add"])
        event_slots_serializer.bulk_update(self.slots_data["change"])
        event_slots_serializer.bulk_delete(self.slots_data["delete"])

        event_price_classes_serializer = EventPriceClassesSerializer()
        event_price_classes_serializer.bulk_create(self.price_classes_data["add"])
        event_price_classes_serializer.bulk_update(self.price_classes_data["change"])
        event_price_classes_serializer.bulk_delete(self.price_classes_data["delete"])

    @staticmethod
    def get_event_id_wise_slot_details(event_ids):
        event_slots = EventSlots.objects.filter(event_id__in=event_ids)

        event_id_wise_slots = defaultdict(list)
        for event_slot in event_slots:
            event_id_wise_slots[event_slot.event_id].append(
                {
                    "id": event_slot.id,
                    "name": event_slot.name,
                    "day_start_time": event_slot.day_start_time,
                    "day_end_time": event_slot.day_end_time
                }
            )
        return event_id_wise_slots

    @staticmethod
    def get_event_id_wise_price_class_details(event_ids):
        event_price_classes = EventPriceClasses.objects.filter(event_id__in=event_ids)

        event_id_wise_price_class_slots = defaultdict(list)
        for event_price_class in event_price_classes:
            event_id_wise_price_class_slots[event_price_class.event_id].append(
                {
                    "id": event_price_class.id,
                    "name": event_price_class.name,
                    "price": event_price_class.price
                }
            )
        return event_id_wise_price_class_slots

    def get(self, product_id):
        self.event_object = Events.objects.get(product_id=product_id)
        self.initialize_product_class(None)

        event_data = self.event_serializer.data
        event_slots_data = self.get_event_id_wise_slot_details([self.event_object.id])
        event_data["slots"] = event_slots_data[self.event_object.id]
        event_price_classes_data = self.get_event_id_wise_price_class_details([self.event_object.id])
        event_data["price_classes"] = event_price_classes_data[self.event_object.id]

        return event_data

    def get_by_ids(self, product_ids):
        events = Events.objects.filter(product_id__in=product_ids)

        event_serializer = EventSerializer(events, many=True)
        events_data = event_serializer.data

        event_ids = []
        for event_data in events_data:
            event_ids.append(event_data["id"])

        event_id_wise_slots_data = self.get_event_id_wise_slot_details(event_ids)
        event_id_wise_price_classes_data = self.get_event_id_wise_price_class_details(event_ids)
        for event_data in events_data:
            event_data["slots"] = event_id_wise_slots_data[event_data["id"]]
            event_data["price_classes"] = event_id_wise_price_classes_data[event_data["id"]]
        return events_data

    def get_sub_products_ids(self, product_ids):
        return {}

    def calculate_starting_prices(self, product_ids, product_ids_with_duration):
        starting_prices = defaultdict()
        for each_product in product_ids:
            each_event_product = product_ids_with_duration[each_product]
            each_event_product_prices = each_event_product["prices"]
            total_price = 0
            for each_price in each_event_product_prices:
                total_price += each_price["price"] * each_price["quantity"]
            starting_prices[each_product] = total_price
        return starting_prices

    def calculate_final_prices(self, products):
        return {}

    def check_valid_duration(self, product_ids, start_time, end_time):
        is_valid = True
        errors = defaultdict(list)
        return is_valid, errors
