from datetime import datetime, date

from django.conf import settings


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
