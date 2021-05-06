from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from .models import Address
from .serializers import AddressSerializer, AddressIdListSerializer
from rest_framework import generics


class AddressList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class AddressDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


def address_details_for_address_ids(address_ids):
    addresses = Address.objects.filter(Q(id__in=address_ids))
    address_serializer = AddressSerializer(addresses, many=True)
    return address_serializer.data


class SpecificAddressList(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request, format=None):
        serializer = AddressIdListSerializer(data=request.data)
        if serializer.is_valid():
            address_details_for_address_ids(serializer.data["ids"])
            return Response()
        else:
            return Response(serializer.errors, 400)

