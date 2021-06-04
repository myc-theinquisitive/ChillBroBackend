from django.core.exceptions import ValidationError
import re


def validate_vehicle_registration_no(vehicle_registration_no):  # Eg: AP 32 DR 6423
    regex = re.compile("^[A-Z|a-z]{2}\s?[0-9]{1,2}\s?[A-Z|a-z]{0,3}\s?[0-9]{4}$")
    if not regex.match(vehicle_registration_no):
        raise ValidationError('Invalid Vehicle Registration Number')
    return True
