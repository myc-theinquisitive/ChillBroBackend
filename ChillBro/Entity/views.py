from django.db.models import Count
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from .constants import VerifiedStatus
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer, \
    EntityVerificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity, EntityVerification
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .wrappers import post_create_address, get_address_details_for_address_ids, get_total_products_count_in_entities
from datetime import datetime
from .helpers import get_date_format
from collections import defaultdict
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, \
    IsEmployee, IsGet, IsEmployeeEntity


def add_verification_details_to_entities(entity_details_list):
    entity_ids = []
    for entity in entity_details_list:
        entity_ids.append(entity["id"])

    entity_verifications = EntityVerification.objects.filter(entity_id__in=entity_ids)
    entity_verification_per_entity_id_dict = {}
    for entity_verification in entity_verifications:
        entity_verification_per_entity_id_dict[entity_verification.entity_id] = entity_verification

    for entity in entity_details_list:
        entity_verification = entity_verification_per_entity_id_dict[entity["id"]]

        employee_name = None
        employee_email = None
        if entity_verification.verified_by:
            employee_name = entity_verification.verified_by.first_name
            employee_email = entity_verification.verified_by.email
        entity["verification"] = {
            "verified_status": entity_verification.verified_status,
            "comments": entity_verification.comments,
            "verified_by": {
                'name': employee_name,
                'email': employee_email
            },
            "updated_at": entity_verification.updated_at.strftime(get_date_format())
        }


def add_address_details_to_entities(entity_details_list):
    address_ids = []
    for entity in entity_details_list:
        address_ids.append(entity["address_id"])

    addresses = get_address_details_for_address_ids(address_ids)
    address_per_address_id = defaultdict(dict)
    for address in addresses:
        address_per_address_id[address["id"]] = address

    for entity in entity_details_list:
        address_id = entity.pop("address_id", None)
        entity["address"] = address_per_address_id[address_id]


class EntityList(generics.ListCreateAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated & (IsSuperAdminOrMYCEmployee | IsBusinessClient), )

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities(response.data["results"])
        add_address_details_to_entities(response.data["results"])
        return response

    def post(self, request, *args, **kwargs):
        if 'city' not in request.data or 'pincode' not in request.data:
            return Response({"message": "City and Pincode are required"}, status=status.HTTP_400_BAD_REQUEST)
    
        address_details = post_create_address(request.data['city'], request.data['pincode'])
        if not address_details['is_valid']:
            return Response({"message": "City or Pincode is invalid", "errors":address_details['errors']}, status=status.HTTP_400_BAD_REQUEST)

        request.data._mutable = True
        request.data['address_id'] = address_details['address_id']

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        entity = serializer.save()

        # Linking entity to business clients
        business_client_entity_data = {
            'entity': entity.id,
            'business_client': request.user.id
        }
        business_client_entity_serializer = BusinessClientEntitySerializer(data=business_client_entity_data)
        if business_client_entity_serializer.is_valid():
            business_client_entity_serializer.save()
        else:
            entity.delete()
            return Response(business_client_entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Entity verification creation
        entity_verification_data = {
            'entity': entity.id
        }
        entity_verification_serializer = EntityVerificationSerializer(data=entity_verification_data)
        if entity_verification_serializer.is_valid():
            entity_verification_serializer.save()
        else:
            entity.delete()
            return Response(entity_verification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "success", "entity_id": entity.id}, status=status.HTTP_200_OK)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | (IsEmployee & IsGet),
                          IsBusinessClientEntity)

    def check_entity_permission(self, request):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return
        self.check_object_permissions(request, entity)

    def get(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities([response.data])
        add_address_details_to_entities([response.data])
        return response

    def post(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        super().post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        super().put(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        # TODO: should only change status of entity here
        super().delete(request, *args, **kwargs)


class EntityListBasedOnVerificationStatus(generics.ListAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee, )

    def get(self, request, *args, **kwargs):
        verified_status = self.kwargs['status']
        if verified_status not in [v_status.value for v_status in VerifiedStatus]:
            return Response({"message": "Can't get entity list",
                             "error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        entity_ids = EntityVerification.objects.filter(verified_status=verified_status)\
            .values_list('entity_id', flat=True)

        self.queryset = MyEntity.objects.filter(id__in=entity_ids).order_by("name")
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities(response.data["results"])
        add_address_details_to_entities(response.data["results"])
        return response


class EntityVerificationDetail(generics.UpdateAPIView):
    queryset = EntityVerification.objects.all()
    serializer_class = EntityVerificationSerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee, )

    def get_object(self):
        return EntityVerification.objects.get(entity_id=self.kwargs['entity_id'])

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['entity_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Entity verification", "error": "Invalid Entity Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if entity.is_verified:
            return Response({"message": "Can't update Entity verification",
                             "error": "Entity is already verified & active"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['entity'] = entity.id
        request.data['verified_by'] = request.user.id
        response = super().put(request, args, kwargs)

        if request.data['verified_status'] == VerifiedStatus.VERIFIED.value:
            # updating verification details for entity
            entity.is_verified = True
            entity.active_from = datetime.now()
            entity.save()

        return response


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


class EntityStatus(APIView):
    serializer_class = EntityStatusSerializer
    permission_classes = (IsAuthenticated,
                          IsSuperAdminOrMYCEmployee | IsBusinessClient, IsBusinessClientEntity | IsEmployeeEntity)

    def put(self, request, pk):
        input_serializer = self.serializer_class(data=request.data)
        if input_serializer.is_valid():
            try:
                queryset = MyEntity.objects.get(id=pk)
            except ObjectDoesNotExist:
                return Response({"message": "Detail not found"}, status=status.HTTP_400_BAD_REQUEST)
            self.check_object_permissions(request, queryset)
            queryset.status = input_serializer.data['status']
            queryset.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessClientEntityList(generics.CreateAPIView):
    queryset = BusinessClientEntity.objects.all()
    serializer_class = BusinessClientEntitySerializer
    permission_classes = (IsAuthenticated, IsBusinessClient,)


class BusinessClientEntities(generics.ListAPIView):
    serializer_class = EntitySerializer
    queryset = BusinessClientEntity.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsOwnerById)

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['bc_id'])
        entity_ids = entity_ids_for_business_client(kwargs['bc_id'])
        entities = MyEntity.objects.filter(id__in=entity_ids)
        serializer = self.serializer_class(entities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def entity_ids_for_business_client(business_client_id):
    entity_ids = BusinessClientEntity.objects.filter(
        business_client_id=business_client_id).values_list('entity_id', flat=True)
    return entity_ids


class CountOfEntitiesAndProducts(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        business_client_entities = BusinessClientEntity.objects.filter(business_client_id=request.user) \
                                    .values_list('entity_id', flat=True)
        business_client_entities_count = business_client_entities.aggregate(count=Count('entity_id'))['count']
        total_products_in_entities = get_total_products_count_in_entities(business_client_entities)
        return Response({'entities_count':business_client_entities_count,\
                         'products_count': total_products_in_entities},200)




