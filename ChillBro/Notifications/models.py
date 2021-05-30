from django.db import models
from .constants import NotificationType, NotificationStatus
from .validations import is_json
import uuid
from .helpers import get_user_model


class Notification(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=36)
    title = models.CharField(max_length=60)
    redirect_url = models.URLField(max_length=256)
    type = models.CharField(choices=[(type.name, type.value) for type in NotificationType], max_length=20)
    status = models.CharField(choices=[(status.name, status.value) for status in NotificationStatus], max_length=20,
                              default=NotificationStatus.ACTIVE.value)
    data = models.TextField(validators=[is_json])
    all_users = models.BooleanField()
    all_business_client = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)


class NotificationUsers(models.Model):
    notification = models.ForeignKey('Notification', on_delete=models.CASCADE)
    user_id = models.CharField(max_length=36)
    status = models.CharField(choices=[(status.name, status.value) for status in NotificationStatus], max_length=20,
                              default=NotificationStatus.ACTIVE.value)

    class Meta:
        unique_together = ('notification', 'user_id')


class NotificationSetting(models.Model):
    user_model = get_user_model()
    created_by = models.OneToOneField(user_model, on_delete=models.CASCADE)
    all = models.BooleanField(default=True)
    bookings = models.BooleanField(default=True)
    payments = models.BooleanField(default=True)
    general = models.BooleanField(default=True)


class FirebaseTokens(models.Model):
    user_model = get_user_model()
    created_by = models.OneToOneField(user_model, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)