from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
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
    addresses = Address.objects.filter(id__in=address_ids)
    address_serializer = AddressSerializer(addresses, many=True)
    return address_serializer.data


class SpecificAddressList(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, format=None):
        serializer = AddressIdListSerializer(data=request.data)
        if serializer.is_valid():
            address_details = address_details_for_address_ids(serializer.data["ids"])
            return Response({"results:": address_details}, 200)
        else:
            return Response({"message": "Can't get address details", "errors:": serializer.errors}, 400)


def get_distance(source,destination):
    source_address = Address.objects.get(id=source)
    source_points = (source_address.longitute,source_address.longitute)
    destination_address = Address.objects.get(id=destination)
    destination_points = (destination_address.longitute,destination_address.longitute)


# def get_multiple_distances():
