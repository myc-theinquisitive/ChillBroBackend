from datetime import datetime, date, timedelta
from .constants import *


def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1


def getEntityType(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities


def getStatus(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status


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
        return week, today + timedelta(1)
    elif date_filter == 'Month':
        today = date.today()
        month = today - timedelta(getTodayDate())
        return month, today + timedelta(1)
    return None, None
