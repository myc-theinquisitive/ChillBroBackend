from django.db import models
from .validations import validate_phone
from django.core.validators import MinLengthValidator
from .constants import SignUpRequestStatus
# Create your models here.


class ReferBusinessClient(models.Model):
    business_type = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    primary_contact = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])
    secondary_contact = models.CharField(max_length=100, validators=[MinLengthValidator(10), validate_phone])
    address = models.TextField()


class SignUpRequest(models.Model):
    business_name = models.CharField(max_length=30)
    client_name = models.CharField(max_length=30)
    contact_number = models.CharField(max_length=10, validators=[MinLengthValidator(10), validate_phone])
    stream = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in SignUpRequestStatus],
                              default=SignUpRequestStatus.YET_TO_VERIFY.value)
