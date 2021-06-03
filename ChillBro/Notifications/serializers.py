from rest_framework import serializers

from .models import Notification, NotificationUsers, NotificationSetting, FirebaseTokens


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class NotificationUsersSerializer(serializers.Serializer):
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
