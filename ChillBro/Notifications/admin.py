from django.contrib import admin
from .models import Notification, NotificationUsers, NotificationSetting, FirebaseTokens

# Register your models here.
admin.site.register(Notification)
admin.site.register(NotificationUsers)
admin.site.register(NotificationSetting)
admin.site.register(FirebaseTokens)
