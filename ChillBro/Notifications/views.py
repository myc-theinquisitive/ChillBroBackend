from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .FCMManager import sendPush
from .constants import NotificationStatus, DEFAULT_SETTINGS
from .models import Notification, NotificationUsers, NotificationSetting, FirebaseTokens
from .serializers import NotificationSerializer, NotificationUsersSerializer, NotificationDeleteSerializer, \
    NotificationSettingSerializer, FirebaseTokensSerializer
import json


class sendNotification(generics.ListAPIView):

    def post(self, request, *args, **kwargs):
        tokens = ["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6ImM2YzkwZmFiMDAwMGI4ODNlMDNjNTY4NDliZGM4MDI5ODQxMzFlNTEifQ.vZ5UrrfsVs-a-S0u1U33I-HRAXse-e2FUULiDeP82oQ"]
        all_tokens = FirebaseTokens.objects.filter(created_by=request.user)
        for each_token in all_tokens:
            tokens.append(each_token.token)
        response = sendPush("Hi", "testing, meesage from vamsi", tokens)
        return Response({"message": "success", "tokens": tokens, "response": str(response)}, 200)


class NotificationCreate(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        request.data['data'] = "{}"
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            dic = request.data.copy()
            try:
                del dic['title'], dic['redirect_url'], dic['type'], dic['status'], \
                    dic['data'], dic['all_users'], dic['all_business_client'], dic['user_ids']
            except:
                pass
            data = json.dumps(dic)
            request.data['data'] = data
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                notification_instance = serializer.save()
                notification_id = notification_instance.id
                if (request.data['all_users'] or request.data['all_business_client']) and (
                        'user_ids' not in request.data or len(request.data['user_ids']) == 0):
                    return Response({"message": "created"}, 201)
                request.data['notification_id'] = notification_id
                notification_users_serializer = NotificationUsersSerializer(data=request.data)
                if not notification_users_serializer.is_valid():
                    notification_instance.delete()
                    return Response(notification_users_serializer.errors, 400)
                for user_id in request.data['user_ids']:
                    NotificationUsers.objects.create(user_id=user_id, notification=notification_instance)
                return Response({"message": "created"}, 201)
            return Response(serializer.errors, 400)
        return Response(serializer.errors, 400)


class BusinessClientNotification(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Notification.objects.filter(all_business_client=True)
        notification_ids = NotificationUsers.objects.filter(user_id=request.user.id,
                                                            status=NotificationStatus.ACTIVE.value).values_list(
            'notification', flat=True)
        self.queryset |= Notification.objects.filter(id__in=notification_ids)
        return super().get(request, *args, **kwargs)


class BusinessClientTypeNotification(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Notification.objects.filter(all_business_client=True, type=self.kwargs['type'])
        notification_ids = NotificationUsers.objects.filter(user_id=request.user.id,
                                                            status=NotificationStatus.ACTIVE.value).values_list(
            'notification', flat=True)
        self.queryset |= Notification.objects.filter(id__in=notification_ids, type=self.kwargs['type'])
        return super().get(request, *args, **kwargs)


class UserNotification(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Notification.objects.filter(all_users=True)
        notification_ids = NotificationUsers.objects.filter(user_id=request.user.id,
                                                            status=NotificationStatus.ACTIVE.value).values_list(
            'notification', flat=True)
        self.queryset |= Notification.objects.filter(id__in=notification_ids)
        return super().get(request, *args, **kwargs)


class UserTypeNotification(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Notification.objects.filter(all_users=True, type=self.kwargs['type'])
        notification_ids = NotificationUsers.objects.filter(user_id=request.user.id,
                                                            status=NotificationStatus.ACTIVE.value).values_list(
            'notification', flat=True)
        self.queryset |= Notification.objects.filter(id__in=notification_ids, type=self.kwargs['type'])
        return super().get(request, *args, **kwargs)


class DeleteNotification(generics.UpdateAPIView):
    queryset = NotificationUsers.objects.all()
    serializer_class = NotificationDeleteSerializer

    def put(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id
        request.data['status'] = NotificationStatus.DELETED.value
        if 'notification' not in request.data:
            return Response({'message': "notification id required"}, 400)
        try:
            NotificationUsers.objects.filter(notification=request.data['notification'],
                                             user_id=request.data['user_id']).update(status=request.data['status'])
            return Response({"message": "Deleted"})
        except:
            return Response({"message": "Detail Not Found"}, 400)


class ChangeSetting(APIView):
    serializer_class = NotificationSettingSerializer
    queryset = NotificationSetting.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            setting = NotificationSetting.objects.get(created_by=request.user)
        except:
            setting["created_by"] = request.user
            serializer = self.serializer_class(setting)
        return Response(serializer.data, 200)

    def put(self, request, *args, **kwargs):
        request.data['created_by'] = request.user.id
        try:
            setting = NotificationSetting.objects.get(created_by=request.user)
            serializer = self.serializer_class(setting, data=request.data)
        except Exception as e:
            serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Success"}, 201)
        return Response(serializer.errors, 400)


class AddOrUpdateFirebaseToken(generics.ListAPIView):

    def post(self, request, *args, **kwargs):
        request.data['created_by'] = request.user

        user_token = FirebaseTokens.objects.filter(created_by=request.user)

        if (len(user_token) == 0):
            serializer = FirebaseTokensSerializer()
            serializer.create(request.data)
        else:
            user_token.update(token=request.data['token'])

        return Response({"message": "Succesfully added"})

