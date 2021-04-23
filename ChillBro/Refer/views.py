from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
# Create your views here.

class ReferBusinessClientList(generics.ListCreateAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer

class ReferBusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferBusinessClient.objects.all()
    serializer_class = ReferBusinessClientSerializer