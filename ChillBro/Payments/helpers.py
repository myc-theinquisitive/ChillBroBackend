from .constants import *
from django.conf import settings
import uuid
from ChillBro.helpers import get_time_period


def get_entity_type(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) == 0:
        return entities
    return entity_filter
    
    
def get_payment_type(payment_filter):
    payment_types = [payment_type.value for payment_type in PayStatus]
    if len(payment_filter) == 0:
        return payment_types
    return payment_filter


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in PayStatus]
    return status


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_transaction_proof(instance, filename):
    id = instance.id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/transaction_proof/%s/%s" % (id, new_filename)
