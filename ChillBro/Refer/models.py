from django.db import models
from .validations import validate_phone
from django.core.validators import MinLengthValidator
from .constants import SignUpRequestStatus, ReferAndEarnStatus
from django.contrib.auth import get_user_model
from datetime import datetime


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


# TODO: Link this creation to signup
class ReferAndEarn(models.Model):
    user_model = get_user_model()
    referred_user = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="referred_user", verbose_name="Referred User")
    referred_by = models.ForeignKey(
        user_model, on_delete=models.CASCADE, related_name="referred_by", verbose_name="Referred By")
    amount_earned = models.IntegerField()
    status = models.CharField(max_length=20, choices=[(status.name, status.value) for status in ReferAndEarnStatus],
                              default=ReferAndEarnStatus.PENDING.value)
    created_on = models.DateTimeField(default=datetime.now)
