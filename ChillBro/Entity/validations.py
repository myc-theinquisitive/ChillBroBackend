from django.core.exceptions import ValidationError
import re
from ChillBro.validations import validate_pan, validate_aadhar, validate_phone, validate_upi_id, \
    validate_ifsc_code, validate_bank_account_no


def validate_gst(gst_in):  # Eg: 37abwpn4366r1ze
    regex = re.compile("\d{2}[A-Za-z]{5}\d{4}[A-Za-z]{1}[0-9A-Z]{1}[zZ]{1}[0-9A-Za-z]{1}")
    if not regex.match(gst_in):
        raise ValidationError(('Invalid GST In'))
    return True


def validate_registration(registration_no):  # U72200MH2009PLC123456
    regex = re.compile("[lLuU][0-9]{5}[A-Za-z]{2}[0-9]{4}[a-zA-Z]{3}[0-9]{6}")
    if not regex.match(registration_no):
        raise ValidationError(('Invalid Registration No'))
    return True
