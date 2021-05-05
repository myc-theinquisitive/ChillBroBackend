import uuid
from datetime import datetime, date, timedelta
from .constants import *

def image_upload_to_review(instance, filename):
    id = instance.review_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/review/%s/%s" % (id, new_filename)


def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1


def getTimePeriod(date_filter):
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
        return week, week + timedelta(7 - getTodayDay())
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, month + timedelta(days_in_months[today.month + 1])
    return None, None

def getEntityType(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities