from channels.db import database_sync_to_async
from .constants import NotificationStatus
from .serializers import NotificationUsersSerializer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.permissions import IsAuthenticated, AllowAny
from .models import NotificationUsers
from djangochannelsrestframework.observer import model_observer


class NotificationCountConsumer(GenericAsyncAPIConsumer):
    queryset = NotificationUsers.objects.all()
    serializer_class = NotificationUsersSerializer
    permission_classes = (AllowAny, )

    @model_observer(NotificationUsers)
    async def notification_user_count_activity(self, notification_count, observer=None, **kwargs):
        await self.send_json({
            "count": notification_count
        })

    @notification_user_count_activity.serializer
    def notification_user_count_activity(self, instance: NotificationUsers, action, **kwargs):
        return NotificationUsersSerializer.get_unread_notifications_count_for_user(instance)

    @notification_user_count_activity.groups_for_signal
    def notification_user_count_activity(self, instance: NotificationUsers, **kwargs):
        # this block of code is called very often *DO NOT make DB QUERIES HERE*
        yield f'-user__{instance.user_id}'  # ! the string **user** is the ``NotificationUsers`` user field.

    @notification_user_count_activity.groups_for_consumer
    def notification_user_count_activity(self, school=None, classroom=None, **kwargs):
        # This is called when you subscribe/unsubscribe
        yield f'-user__{kwargs["user_id"]}'

    @action()
    async def subscribe_to_notification_activity(self, user_id, **kwargs):
        # We will check if the user is authenticated for subscribing.
        kwargs["user_id"] = user_id
        await self.notification_user_count_activity.subscribe(user_id=user_id)
