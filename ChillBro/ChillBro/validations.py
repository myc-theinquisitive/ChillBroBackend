from django.core.exceptions import ValidationError
import re


def validate_pan(pan_no):  # Eg: abwpn4366r
    regex = re.compile("[A-Za-z]{5}\d{4}[A-Za-z]{1}")
    if not regex.match(pan_no):
        raise ValidationError(('Invalid Pan Number'))
    return True


def validate_aadhar(aadhar_no): # 4444 3333 2222
    regex = re.compile("[2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4}")
    if not regex.match(aadhar_no):
        raise ValidationError(('Invalid AadharNo'))
    return True


def validate_bank_account_no(account_no): # 1010101010
    regex = re.compile("[0-9]{9,18}")
    if not regex.match(account_no):
        raise ValidationError('Invalid Account Number')
    return True


def validate_ifsc_code(ifsc_code):  # SBIN0125620
    regex = re.compile("[A-Z]{4}0[A-Z0-9]{6}")
    if not regex.match(ifsc_code):
        raise ValidationError('Invalid IFSC Code')
    return True


def validate_upi_id(upi_id): #9898989898@ybl
    regex = re.compile("[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}")
    if not regex.match(upi_id):
        raise ValidationError('Invalid UPI ID')
    return True


def validate_phone(phone):
    if len(phone) != 10:
        return False
    if len(list(filter(lambda x: not x.isdigit(), phone))) > 0:
        raise ValidationError('Characters not allowed')
    if phone[0] not in ['6', '7', '8', '9']:
        raise ValidationError('First digit should be in (6,7,8,9). But %(value)  given',
                              params={'value': int(phone[0])}, )
    return True


def validate_email(email): #admin@theinquisitive.in
    regex = re.compile("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}")
    if not regex.match(email):
        raise ValidationError('Invalid Email')
    return True