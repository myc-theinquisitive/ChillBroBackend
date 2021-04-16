from django.core.exceptions import ValidationError

def validate_phone(phone):
    if len(phone)!=10:
        return False
    if len(list(filter(lambda  x: not x.isdigit(),phone)))>0:
        raise ValidationError(('Characters not allowed'))
    if phone[0] not in ['6','7','8','9']:
        raise ValidationError(('First digit should be in (6,7,8,9). But %(value)  given'),params={'value': int(phone[0])},)
    return True