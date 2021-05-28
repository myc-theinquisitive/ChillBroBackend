from django.conf import settings
from .constants import EntityType, EntitySubType


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_entity_types(entity_filters):
    if len(entity_filters) != 0:
        return entity_filters

    entities = [entity_type.value for entity_type in EntityType]
    entities.append(None)
    return entities


def get_entity_sub_types(sub_entity_filters):
    if len(sub_entity_filters) != 0:
        return sub_entity_filters

    sub_entities = [entity_sub_type.value for entity_sub_type in EntitySubType]
    sub_entities.append(None)
    return sub_entities
