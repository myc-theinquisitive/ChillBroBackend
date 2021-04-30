from django.conf import settings
from .constants import EntityType


def get_user_model():
    return settings.AUTH_USER_MODEL


def getEntityType(entity_filters):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filters) != 0:
        return entity_filters
    return entities