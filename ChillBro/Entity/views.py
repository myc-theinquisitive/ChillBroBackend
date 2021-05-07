from django.db.models import F
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer, AddressSerializer, \
    EntityAccountSerializer, EntityUPISerializer, EntityEditSerializer
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity, EntityUPI, EntityAccount
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .wrappers import create_address
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, \
    IsEmployee, IsGet, IsEmployeeEntity



class EntityList(generics.CreateAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated, IsBusinessClient,)

    def post(self, request, *args, **kwargs):
        serializer = AddressSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        response_from_address = create_address(request.data['city'], request.data['pincode'])
        if response_from_address['is_valid']:
            request.data['address_id'] = response_from_address["address_id"]
            entity_upi_serializer = EntityUPISerializer(data=request.data)
            entity_account_serializer = EntityAccountSerializer(data=request.data)
            if not entity_account_serializer.is_valid():
                return Response(entity_account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if not entity_upi_serializer.is_valid():
                return Response(entity_upi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            upi_instance = entity_upi_serializer.save()
            account_instance = entity_account_serializer.save()
            request.data['account'] = account_instance.id
            request.data['upi'] = upi_instance.id
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                entity_instance = serializer.save()
                entity_id = serializer.data['id']
                request.data['entity_id'] = entity_id
                request.data['business_client_id'] = request.user.id
                business_client_entity_serializer = BusinessClientEntitySerializer(data=request.data)
                if business_client_entity_serializer.is_valid():
                    business_client_entity_instance = business_client_entity_serializer.save()

                    return Response({"message": "success"}, status=status.HTTP_200_OK)
                else:
                    entity_instance.delete()
                    return Response(business_client_entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "City or Pincode is invalid", "errors": response_from_address["errors"]},
                            status=status.HTTP_400_BAD_REQUEST)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | (IsEmployee & IsGet), IsBusinessClientEntity)

    def check_entity_permission(self, request):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['pk'])
            self.check_object_permissions(request, entity)
        except:
            pass

    def get(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = MyEntity.objects.filter(id=self.kwargs['pk']) \
            .values('id', 'name', 'type', 'status', 'address_id', 'active_from', 'pan_no', 'registration_no',
                    'gst_in', 'aadhar_no', 'pan_image', 'registration_image', 'gst_image','aadhar_image',
                    bank_name=F('account__bank_name'), account_no=F('account__account_no'), ifsc_code=F('account__ifsc_code'),
                    account_type=F('account__account_type'), account_holder_name=F('account__account_holder_name'),
                    pay_tm=F('upi__pay_tm'), phone_pe=F('upi__phone_pe'), g_pay=F('upi__g_pay'),upiid=F('upi__upi_id')).get()
        return Response(entity)

    def put(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = MyEntity.objects.get(id=self.kwargs['pk'])
        serializer = EntityEditSerializer(entity, data=request.data)
        account_id = entity.account_id
        upi_id = entity.upi_id
        account = EntityAccount.objects.get(id=account_id)
        upi = EntityUPI.objects.get(id=upi_id)
        account_serializer = EntityAccountSerializer(account, data=request.data)
        upi_serializer = EntityUPISerializer(upi, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not account_serializer.is_valid():
            return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not upi_serializer.is_valid():
            return Response(upi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        account_serializer.save()
        upi_serializer.save()
        return Response({"message": "Updated"})

    def delete(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        super().delete(request, *args, **kwargs)


class EntityStatusAll(generics.GenericAPIView):
    serializer_class = EntityStatusSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient)

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            entity_ids = BusinessClientEntity.objects.filter(business_client_id=request.user.id).values_list(
                'entity_id', flat=True)
            queryset = MyEntity.objects.filter(id__in=entity_ids)
            queryset.update(status=serializer.data['status'])
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntityStatus(generics.GenericAPIView):
    serializer_class = EntityStatusSerializer
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsBusinessClientEntity | IsEmployeeEntity)

    def put(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                queryset = MyEntity.objects.get(id=pk)
            except:
                return Response({"message": "Detail not found"}, status=status.HTTP_400_BAD_REQUEST)
            self.check_object_permissions(request, queryset)
            queryset.status = serializer.data['status']
            queryset.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessClientEntityList(generics.CreateAPIView):
    queryset = BusinessClientEntity.objects.all()
    serializer_class = BusinessClientEntitySerializer
    permission_classes = (IsAuthenticated, IsBusinessClient,)


class BusinessClientEntities(generics.ListAPIView):
    serializer_class = EntitySerializer
    queryset = BusinessClientEntity.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsOwnerById)

    def get(self, request, bc_id):
        self.check_object_permissions(request, bc_id)
        entity_ids = get_entity_ids_for_business_client(self.kwargs['bc_id'])
        entities = MyEntity.objects.filter(id__in=entity_ids)
        serializer = self.serializer_class(entities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def get_entity_ids_for_business_client(business_client_id):
    entity_ids = BusinessClientEntity.objects.filter(business_client_id=business_client_id).values_list('entity_id',
                                                                                                        flat=True)
    return entity_ids
