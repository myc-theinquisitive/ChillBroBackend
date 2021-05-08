from .views import entity_ids_for_business_client
from .models import MyEntity


def get_entity_ids_for_business_client(business_client_id):
    return entity_ids_for_business_client(business_client_id)


def is_entity_id_exist(entity_id):
    return True
    # try:
    #     entity = MyEntity.objects.get(id = entity_id)
    # except:
    #     return False
    # return True
