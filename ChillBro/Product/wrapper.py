from taggit.managers import TaggableManager
import kvstore
from kvstore.model_admin import TagInline
from kvstore.models import ContentType, Tag


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
