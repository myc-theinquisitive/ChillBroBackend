from Entity.export_apis import get_entity_ids_for_business_client as entity_ids
from authentication.views import Logout

def get_entity_ids_for_business_client(business_client_id):
    return entity_ids(business_client_id)

def logout(request):
    Logout.get(request)