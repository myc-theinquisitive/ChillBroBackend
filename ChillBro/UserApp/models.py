from django.db import models
from authentication.models import EmailUserManager, EmailAbstractUser


class MyUser(EmailAbstractUser):
    # Custom fields
    date_of_birth = models.DateField('Date of birth', null=True, blank=True)

    # Required
    objects = EmailUserManager()

