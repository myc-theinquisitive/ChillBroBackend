from taggit.managers import TaggableManager
import kvstore
from kvstore.model_admin import TagInline
from kvstore.models import ContentType, Tag
from Bookings.exportapi import booked_count_of_product_id


def get_taggable_manager():
    return TaggableManager()


def get_key_value_store():
    return kvstore


def get_key_value_taggable_inline():
    return TagInline


def key_value_content_type_model():
    return ContentType


def key_value_tag_model():
    return Tag


def get_booked_count_of_product_id(product_id, from_date, to_date):
    return booked_count_of_product_id(product_id, from_date, to_date)