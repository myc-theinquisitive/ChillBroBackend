from datetime import date, timedelta, datetime
from django.conf import settings


def get_today_day():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def get_today_date():
    today = date.today().strftime("%d")
    return int(today) - 1


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
        week = today - timedelta(get_today_day())
        return week, week + timedelta(7 - get_today_day())
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(get_today_date())
        return month, month + timedelta(days_in_months[today.month+1])
    return None, None


def get_previous_time_period(date_filter):
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
        week = today - timedelta(get_today_day())
        previous_week = week - timedelta(7)
        return previous_week, week
    elif date_filter == 'Month':
        days_in_months = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        today = date.today()
        month = today - timedelta(get_today_date())
        previous_month = month - timedelta(days_in_months[today.month] + 1)
        return previous_month, month


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"