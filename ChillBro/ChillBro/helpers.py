from datetime import date, timedelta, datetime
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .constants import DateFilters
from dateutil.relativedelta import relativedelta


def get_storage():
    storage_path = settings.DEFAULT_FILE_STORAGE if hasattr(settings, 'DEFAULT_FILE_STORAGE') else ""
    return FileSystemStorage(storage_path)


def get_today_day():
    day = datetime.now().weekday()
    if day == 6:
        return 0
    return day + 1


def get_today_date():
    today = date.today().strftime("%d")
    return int(today) - 1


# function returns the dates for the given time frame
# first value is inclusive and second value is exclusive
def get_time_period(date_filter):
    today = date.today()
    if date_filter == DateFilters.TOTAL.value:
        return None, None
    elif date_filter == DateFilters.TODAY.value:
        tomorrow = today + timedelta(1)
        return today, tomorrow
    elif date_filter == DateFilters.YESTERDAY.value:
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == DateFilters.THIS_WEEK.value:
        week_start = today - timedelta(get_today_day())
        return week_start, week_start + timedelta(7)
    elif date_filter == DateFilters.THIS_MONTH.value:
        month_start = today - timedelta(get_today_date())
        return month_start, month_start + relativedelta(months=+1)
    elif date_filter == DateFilters.LAST_7_DAYS.value:
        end_time = today + timedelta(1)
        start_time = today - timedelta(6)
        return start_time, end_time
    elif date_filter == DateFilters.LAST_30_DAYS.value:
        end_time = today + timedelta(1)
        start_time = today - timedelta(29)
        return start_time, end_time
    elif date_filter == DateFilters.LAST_6_MONTHS.value:
        last_six_months = date.today() + relativedelta(months=-6) + timedelta(1)
        tomorrow = today + timedelta(1)
        return last_six_months, tomorrow
    return None, None


# function returns the dates for the given time frame
# first value is inclusive and second value is exclusive
def get_previous_time_period(date_filter):
    today = date.today()
    if date_filter == DateFilters.TOTAL.value:
        return None, None
    elif date_filter == DateFilters.TODAY.value:
        yesterday = today - timedelta(1)
        return yesterday, today
    elif date_filter == DateFilters.YESTERDAY.value:
        yesterday = today - timedelta(1)
        day_before_yesterday = today - timedelta(2)
        return day_before_yesterday, yesterday
    elif date_filter == DateFilters.THIS_WEEK.value:
        week = today - timedelta(get_today_day())
        previous_week = week - timedelta(7)
        return previous_week, week
    elif date_filter == DateFilters.THIS_MONTH.value:
        month = today - timedelta(get_today_date())
        previous_month = month + relativedelta(months=-1)
        return previous_month, month
    elif date_filter == DateFilters.LAST_7_DAYS.value:
        end_time = today - timedelta(6)
        start_time = today - timedelta(13)
        return start_time, end_time
    elif date_filter == DateFilters.LAST_30_DAYS.value:
        end_time = today - timedelta(29)
        start_time = today - timedelta(59)
        return start_time, end_time
    elif date_filter == DateFilters.LAST_6_MONTHS.value:
        last_twelve_months = date.today() + relativedelta(months=-12)
        last_six_months = date.today() + relativedelta(months=-6) + timedelta(1)
        return last_twelve_months, last_six_months
    return None, None


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"
