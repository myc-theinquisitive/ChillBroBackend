from django.core.exceptions import ObjectDoesNotExist
from .views import entity_ids_for_user, get_entity_details, filter_entity_ids_by_city
from .models import MyEntity


def get_entity_ids_for_business_client(business_client_id):
    return entity_ids_for_user(business_client_id)


def is_entity_id_exist(entity_id):
    try:
        entity = MyEntity.objects.get(id=entity_id)
    except ObjectDoesNotExist:
        return False
    return True


def get_entity_details_for_entity_ids(entity_ids):
    return get_entity_details(entity_ids)


def get_entity_type_and_sub_type(entity_id):
    try:
        entity_types = MyEntity.objects.get(id=entity_id)
        return entity_types.type, entity_types.sub_type
    except ObjectDoesNotExist:
        return None, None
