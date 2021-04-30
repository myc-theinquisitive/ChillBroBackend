from datetime import datetime, date, timedelta
from django.conf import settings
import uuid
from .constants import *


def getTodayDay():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def getTodayDate():
    today = date.today().strftime("%d")
    return int(today) - 1


def get_user_model():
    return settings.AUTH_USER_MODEL


def image_upload_to_user_id_proof(instance, filename):
    id = instance.booking.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/users_id_proof/%s/%s" % (id, new_filename)


def image_upload_to_check_in(instance, filename):
    id = instance.check_in.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_in/%s/%s" % (id, new_filename)


def image_upload_to_check_out(instance, filename):
    id = instance.check_out.booking_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return "static/images/check_out/%s/%s" % (id, new_filename)


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_entity_types_filter(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities


def get_time_period(date_filter):
    if date_filter == 'Total':
        return None, None
    elif date_filter == 'Today':
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
        return month, month + timedelta(days_in_months[today.month+1])
    return None, None


def getPreviousTimePeriod(date_filter):
    if date_filter == 'Total':
        return None, None
    elif date_filter == 'Today':
        today = date.today()
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == 'Yesterday':
        today = date.today()
        yesterday = today - timedelta(1)
        day_before_yesterday = today - timedelta(2)
        return day_before_yesterday, yesterday
    elif date_filter == 'Week':
        today = date.today()
        week = today - timedelta(getTodayDay())
        previous_week = week - timedelta(7)
        return previous_week, week
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(getTodayDate())
        previous_month = month - timedelta(days_in_months[today.month] + 1)
        return previous_month, month


def get_status_filters(status):
    if len(status) == 0:
        return [status.value for status in BookingStatus]
    return status

