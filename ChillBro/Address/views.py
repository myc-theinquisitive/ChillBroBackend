from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Address, UserSavedAddress
from .serializers import AddressSerializer, AddressIdListSerializer, SavedAddressSerializer
from rest_framework import generics, status


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
            return Response({"message": "Can't get address details", "errors": serializer.errors}, 400)


class UserSavedAddressView(APIView):
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request, format=None):
        request.data["created_by"] = request.user.id
        saved_address_serializer = SavedAddressSerializer(data=request.data)

        from .helpers import create_address
        response_dict = create_address(request.data["address"])
        if not response_dict["is_valid"]:
            return Response({"message": "Can't create address",
                             "errors:": response_dict["errors"]}, 400)

        request.data["address"] = response_dict["address_id"]
        if saved_address_serializer.is_valid():
            saved_address_serializer.save()
            return Response({"message": "Address created successfully",
                             "address_id:": response_dict["address_id"]}, 200)
        else:
            return Response({"message": "Can't create address",
                             "errors": saved_address_serializer.errors}, 400)

    def get(self, request, *args, **kwargs):
        user_saved_addresses = UserSavedAddress.objects.select_related('address')\
            .filter(created_by=request.user)

        address_detail_dicts = []
        for user_saved_address in user_saved_addresses:
            address_detail_dict = {
                "address": AddressSerializer(user_saved_address.address).data,
                "address_type": user_saved_address.address_type
            }
            address_detail_dicts.append(address_detail_dict)

        return Response({"results": address_detail_dicts}, 200)


class UserSavedAddressDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        try:
            saved_address = UserSavedAddress.objects.get(
                created_by=request.user, address_id=self.kwargs["address_id"])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update address",
                             "errors": "Invalid address id for user"}, 400)

        from .helpers import update_address
        response_dict = update_address(self.kwargs["address_id"], request.data["address"])
        if not response_dict["is_valid"]:
            return Response({"message": "Can't update address",
                             "errors:": response_dict["errors"]}, 400)

        request.data["address"] = self.kwargs["address_id"]
        saved_address_serializer = SavedAddressSerializer(saved_address, data=request.data)
        if saved_address_serializer.is_valid():
            saved_address_serializer.save()
            return Response({"message": "Address updated successfully",
                             "address_id:": response_dict["address_id"]}, 200)
        else:
            return Response({"message": "Can't update address",
                             "errors": saved_address_serializer.errors}, 400)

    def delete(self, request, *args, **kwargs):
        request.data["created_by"] = request.user.id
        try:
            saved_address = UserSavedAddress.objects.get(
                created_by=request.user, address_id=self.kwargs["address_id"])
        except ObjectDoesNotExist:
            return Response({"message": "Can't delete address",
                             "errors": "Invalid address id for user"}, 400)

        saved_address.delete()
        return Response({"message": "Address deleted successfully"}, 200)


def get_distance(source, destination):
    source_address = Address.objects.get(id=source)
    source_points = (source_address.longitute, source_address.longitute)
    destination_address = Address.objects.get(id=destination)
    destination_points = (destination_address.longitute, destination_address.longitute)


# def get_multiple_distances():
