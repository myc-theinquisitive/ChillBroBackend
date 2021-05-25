import uuid
from datetime import datetime, date, timedelta

from django.conf import settings

from .constants import *


def get_media_root():
    return settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else ""


def image_upload_to_review(instance, filename):
    id = instance.review_id
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (id, str(uuid.uuid4()), file_extension)
    return get_media_root() + "static/images/review/%s/%s" % (id, new_filename)


def get_today_day():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def get_today_date():
    today = date.today().strftime("%d")
    return int(today) - 1


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
        week = today - timedelta(get_today_day())
        return week, week + timedelta(7 - get_today_day())
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(get_today_date())
        return month, month + timedelta(days_in_months[today.month + 1])
    return None, None


def get_entity_type(entity_filter):
    entities = [entity_type.value for entity_type in EntityType]
    if len(entity_filter) != 0:
        return entity_filter
    return entities
    
def get_rating_filters(rating_filter):
    ratings = [rating for rating in range(1,6)]
    if len(rating_filter) == 0:
        return ratings
    return rating_filter


def get_categories(category_filters):
    categories = [category.value for category in FeedbackCategory]
    if len(category_filters)==0:
        return categories
    if category_filters[0] == "ALL":
        return categories
    return category_filters