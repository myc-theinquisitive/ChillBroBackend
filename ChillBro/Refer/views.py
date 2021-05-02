from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import *
from .serializers import *
from .constants import SHARE_APP_MESSAGE
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient

# Create your views here.

class ReferBusinessClientList(generics.ListCreateAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient)

class ReferBusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee,)

class ShareApp(APIView):
    def get(self,request):
        return Response({"message":SHARE_APP_MESSAGE})