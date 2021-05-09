from .views import entity_ids_for_business_client, get_entity_details
from .models import MyEntity


def get_entity_ids_for_business_client(business_client_id):
    return entity_ids_for_business_client(business_client_id)


def is_entity_id_exist(entity_id):
    try:
        entity = MyEntity.objects.get(id = entity_id)
    except:
        return False
    return True


def get_entity_details_for_entity_ids(entity_ids):
    return get_entity_details(entity_ids)
