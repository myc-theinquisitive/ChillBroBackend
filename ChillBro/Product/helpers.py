from django.conf import settings
from .BaseProduct.constants import ActivationStatus


def get_date_format():
    return settings.DATE_FORMAT if hasattr(settings, 'DATE_FORMAT') else "%Y-%m-%dT%H:%M:%S"


def get_status(statuses):
    all_statuses = [each_status.value for each_status in ActivationStatus]
    if len(statuses) == 0:
        return all_statuses
    return statuses

