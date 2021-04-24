from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import *
from .serializers import *
from .constants import SHARE_APP_MESSAGE
from rest_framework.views import APIView

# Create your views here.

class ReferBusinessClientList(generics.ListCreateAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer

class ReferBusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer

class ShareApp(APIView):
    def get(self,request):
        return Response({"message":SHARE_APP_MESSAGE})