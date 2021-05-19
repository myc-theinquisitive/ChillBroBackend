from django.core.exceptions import ObjectDoesNotExist

from .views import entity_ids_for_user, get_entity_details
from .models import MyEntity


def get_entity_ids_for_business_client(business_client_id):
    return entity_ids_for_user(business_client_id)


def is_entity_id_exist(entity_id):
    try:
        entity = MyEntity.objects.get(id = entity_id)
    except ObjectDoesNotExist:
        return False
    return True


def get_entity_details_for_entity_ids(entity_ids):
    return get_entity_details(entity_ids)


def filter_entity_ids_by_city(entity_ids, city):
    from .wrappers import filter_address_ids_by_city
    address_ids = MyEntity.objects.filter(id__in=entity_ids).values_list("address_id", flat=True)
    city_address_ids = filter_address_ids_by_city(address_ids, city)
    return MyEntity.objects.filter(id__in=entity_ids, address_id__in=city_address_ids)\
        .values_list("id", flat=True)
