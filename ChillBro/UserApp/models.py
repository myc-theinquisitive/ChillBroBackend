from django.db import models
from authentication.models import EmailUserManager, EmailAbstractUser


class MyUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField('Date of birth', null=True, blank=True)
    phone_number=models.CharField('phone_number',max_length=10)

    # Required
    objects = EmailUserManager()

