from datetime import datetime, date, timedelta
from .constants import *
from django.conf import settings
import uuid

def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1


def get_entity_type(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) == 0:
        return entities
    return entity_filter


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in PayStatus]
    return status


def get_time_period(date_filter):
    if date_filter == 'Today':
        today = date.today()
        tomorrow = today + timedelta(1)
        return today, tomorrow
    elif date_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        return week, today + timedelta(1)
    elif date_filter == 'Month':
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, today + timedelta(1)
    return None, None


def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload_to_transaction_proof(instance, filename):
    id = instance.id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/transaction_proof/%s/%s" % (id, new_filename)

