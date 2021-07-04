from rest_framework import serializers

from .constants import NotificationStatus
from .models import Notification, NotificationUsers, NotificationSetting, FirebaseTokens


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUsers
        fields = '__all__'

    @staticmethod
    def get_unread_notifications_count_for_user(instance):
        return NotificationUsers.objects.filter(
            user_id=instance.user_id, status=NotificationStatus.ACTIVE.value).count()


class UserIdsSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.CharField(min_length=36, max_length=36)
    )


class NotificationDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationUsers
        fields = '__all__'


class NotificationSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSetting
        fields = '__all__'


class FirebaseTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseTokens
        fields = '__all__'
