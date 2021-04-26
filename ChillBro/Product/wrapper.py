from taggit.managers import TaggableManager
import kvstore
from kvstore.model_admin import TagInline
from kvstore.models import ContentType, Tag
from Bookings.exportapi import bookedCountOfProductId


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


def getBookedCountOfProductId(product_id, from_date, to_date):
    return bookedCountOfProductId(product_id, from_date, to_date)