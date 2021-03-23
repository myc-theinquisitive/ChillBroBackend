
from .models import *
from .serializers import TransportSerializer
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class TransportsList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    queryset = Transport.objects.all()
    serializer_class = TransportSerializer


class TransportsDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    queryset = Transport.objects.all()
    serializer_class = TransportSerializer

