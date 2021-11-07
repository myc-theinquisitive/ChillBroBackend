from django.conf import settings


def get_user_model():
    return settings.AUTH_USER_MODEL


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_day_format():
    return "%Y-%m-%d"