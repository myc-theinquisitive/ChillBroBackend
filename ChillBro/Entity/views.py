import json
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from .constants import ActivationStatus, EntityTypes
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer, \
    EntityVerificationSerializer, EntityAccountSerializer, EntityUPISerializer, EntityEditSerializer, \
    EntityDetailsSerializer, EntityVerificationUpdateInputSerializer, GetEntitiesByStatusSerializer, \
    EntityRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity, EntityVerification, EntityUPI, EntityAccount, EntityRegistration
from rest_framework.response import Response
from rest_framework import status
from .wrappers import post_create_address, get_address_details_for_address_ids, get_total_products_count_in_entities, \
    update_address_for_address_id, get_entity_id_wise_employees, get_entity_ids_for_employee, get_top_level_categories
from datetime import datetime
from .helpers import get_date_format, get_entity_status
from collections import defaultdict
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, \
    IsEmployee, IsGet, IsEmployeeEntity


def entity_ids_for_user(user_id):
    entity_ids = BusinessClientEntity.objects.filter(
        business_client_id=user_id).values_list('entity_id', flat=True)
    if len(entity_ids) == 0:
        entity_ids = get_entity_ids_for_employee(user_id)
    return entity_ids


def get_entity_details(entity_ids):
    entities = MyEntity.objects.filter(id__in=entity_ids)
    entities_data = EntitySerializer(entities, many=True).data
    add_address_details_to_entities(entities_data)
    return entities_data


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
    permission_classes = (IsAuthenticated & (IsSuperAdminOrMYCEmployee | IsBusinessClient),)

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities(response.data["results"])
        add_address_details_to_entities(response.data["results"])
        return response

    def post(self, request, *args, **kwargs):
        request_data = request.data.dict()
        address_data = request_data.pop('address', {})
        address_data = json.loads(address_data)

        address_details = post_create_address(address_data)
        if not address_details['is_valid']:
            return Response({"message": "Can't create outlet", "errors": address_details['errors']},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data._mutable = True
        request.data['address_id'] = address_details['address_id']

        entity_registration_serializer = EntityRegistrationSerializer(data=request.data)
        entity_upi_serializer = EntityUPISerializer(data=request.data)
        entity_account_serializer = EntityAccountSerializer(data=request.data)
        if not entity_registration_serializer.is_valid():
            return Response({"message": "Can't create outlet", "errors": entity_registration_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        if not entity_account_serializer.is_valid():
            return Response({"message": "Can't create outlet", "errors": entity_account_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        if not entity_upi_serializer.is_valid():
            return Response({"message": "Can't create outlet", "errors": entity_upi_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        registration_instance = entity_registration_serializer.save()
        upi_instance = entity_upi_serializer.save()
        account_instance = entity_account_serializer.save()
        request.data['registration'] = registration_instance.id
        request.data['account'] = account_instance.id
        request.data['upi'] = upi_instance.id

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Can't create outlet", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"message": "Can't create outlet", "errors": business_client_entity_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        # Entity verification creation
        entity_verification_data = {
            'entity': entity.id
        }
        entity_verification_serializer = EntityVerificationSerializer(data=entity_verification_data)
        if entity_verification_serializer.is_valid():
            entity_verification_serializer.save()
        else:
            entity.delete()
            return Response({"message": "Can't create outlet", "errors": entity_verification_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Outlet created successfully", "entity_id": entity.id},
                        status=status.HTTP_201_CREATED)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | (IsEmployee & IsGet), IsBusinessClientEntity)

    def check_entity_permission(self, request):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return
        self.check_object_permissions(request, entity)

    def get(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = MyEntity.objects.select_related('account', 'upi', 'registration').get(id=self.kwargs['pk'])
        serializer = EntityDetailsSerializer(entity)

        response_data = serializer.data
        add_verification_details_to_entities([response_data])
        add_address_details_to_entities([response_data])

        return Response({"results": response_data}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = MyEntity.objects.get(id=self.kwargs['pk'])
        if entity.activation_status == ActivationStatus.DELETED.value:
            return Response({"message": "Can't update outlet details",
                             "errors": "Entity is already deleted"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EntityEditSerializer(entity, data=request.data)

        address_data = request.data.dict().pop("address", {})
        address_data = json.loads(address_data)
        address_id = entity.address_id
        address_details = update_address_for_address_id(address_id, address_data)
        if not address_details['is_valid']:
            return Response({"message": "Can't update outlet details", "errors": address_details['errors']},
                            status=status.HTTP_400_BAD_REQUEST)

        registration = EntityRegistration.objects.get(id=entity.registration_id)
        account = EntityAccount.objects.get(id=entity.account_id)
        upi = EntityUPI.objects.get(id=entity.upi_id)

        registration_serializer = EntityRegistrationSerializer(registration, data=request.data)
        account_serializer = EntityAccountSerializer(account, data=request.data)
        upi_serializer = EntityUPISerializer(upi, data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Can't update outlet details",
                             "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if not registration_serializer.is_valid():
            return Response({"message": "Can't update outlet details",
                             "errors": registration_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if not account_serializer.is_valid():
            return Response({"message": "Can't update outlet details",
                             "errors": account_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if not upi_serializer.is_valid():
            return Response({"message": "Can't update outlet details",
                             "errors": upi_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        registration_serializer.save()
        account_serializer.save()
        upi_serializer.save()
        return Response({"message": "Outlet details updated successfully"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = self.get_object()
        entity.activation_status = ActivationStatus.DELETED.value
        entity.save()
        return Response({"message": "Outlet deleted successfully"}, status=status.HTTP_200_OK)


class EntityListBasedOnVerificationStatus(generics.ListAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    def get(self, request, *args, **kwargs):
        activation_status = self.kwargs['status']
        if activation_status not in [v_status.value for v_status in ActivationStatus]:
            return Response({"message": "Can't get outlet list",
                             "errors": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        self.queryset = MyEntity.objects.filter(activation_status=activation_status).order_by("name")
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities(response.data["results"])
        add_address_details_to_entities(response.data["results"])
        return response


class EntityVerificationDetail(generics.RetrieveUpdateAPIView):
    queryset = EntityVerification.objects.all()
    serializer_class = EntityVerificationSerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    def get_object(self):
        return EntityVerification.objects.get(entity_id=self.kwargs['entity_id'])

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['entity_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Outlet verification", "error": "Invalid Outlet Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if entity.activation_status == ActivationStatus.ACTIVE.value:
            return Response({"message": "Can't update Outlet verification",
                             "errors": "Outlet is already verified & active"}, status=status.HTTP_400_BAD_REQUEST)
        elif entity.activation_status == ActivationStatus.DELETED.value:
            return Response({"message": "Can't update Outlet verification",
                             "errors": "Outlet is deleted"}, status=status.HTTP_400_BAD_REQUEST)

        input_serializer = EntityVerificationUpdateInputSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't update Outlet verification",
                             "errors": input_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        request.data['entity'] = entity.id
        request.data['verified_by'] = request.user.id
        super().put(request, args, kwargs)

        activation_status = request.data['activation_status']
        if activation_status == ActivationStatus.ACTIVE.value:
            # updating verification details for entity
            entity.is_verified = True
            entity.active_from = datetime.now()
        entity.activation_status = activation_status
        entity.save()

        return Response({"message": "Outlet verified successfully"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['entity_id'])
        except ObjectDoesNotExist:
            return Response({"message": "detail not found", "error": "Invalid Outlet Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = EntitySerializer(entity)
        response_data = serializer.data
        add_verification_details_to_entities([response_data])
        add_address_details_to_entities([response_data])
        return Response(response_data, status=status.HTTP_200_OK)


class EntityStatusAll(generics.GenericAPIView):
    serializer_class = EntityStatusSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee)

    def put(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Can't update Outlet status",
                             "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        entity_ids = entity_ids_for_user(request.user.id)
        entities = MyEntity.objects.active().filter(id__in=entity_ids)
        entities.update(status=serializer.data['status'])
        return Response({"message": "Outlet status updated successfully"}, status=status.HTTP_200_OK)

    def get(self, request):
        entity_ids = entity_ids_for_user(request.user.id)
        statuses = MyEntity.objects.filter(id__in=entity_ids).values('id', 'status', 'name')
        return Response(statuses, 200)


class EntityStatus(APIView):
    serializer_class = EntityStatusSerializer
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsBusinessClientEntity | IsEmployeeEntity)

    def put(self, request, pk):
        input_serializer = self.serializer_class(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't update Outlet status",
                             "errors": input_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = MyEntity.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Outlet status",
                             "errors": "Invalid Outlet Id"}, status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, entity)

        if entity.activation_status != ActivationStatus.ACTIVE.value:
            return Response({"message": "Can't update Outlet status",
                             "errors": "Outlet is not active"}, status=status.HTTP_400_BAD_REQUEST)

        entity.status = input_serializer.data['status']
        entity.save()
        return Response({"message": "Outlet status updated successfully"}, status=status.HTTP_200_OK)


class BusinessClientEntities(generics.ListAPIView):
    serializer_class = EntitySerializer
    queryset = BusinessClientEntity.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,)

    def get(self, request, *args, **kwargs):
        entity_ids = entity_ids_for_user(request.user.id)
        entities = MyEntity.objects.active().filter(id__in=entity_ids)
        serializer = self.serializer_class(entities, many=True)

        # Adding Employees for entity
        entity_id_wise_employees = get_entity_id_wise_employees(entity_ids)
        for entity in serializer.data:
            entity["employees"] = entity_id_wise_employees[entity["id"]]

        return Response(serializer.data, status=status.HTTP_200_OK)


class BusinessClientEntitiesByVerificationStatus(generics.ListAPIView):
    serializer_class = EntitySerializer
    queryset = MyEntity.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,)

    def post(self, request, *args, **kwargs):
        input_serializer = GetEntitiesByStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get entities", "errors": input_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
        
        entity_ids = request.data['entity_ids']
        activation_statuses = get_entity_status(request.data['statuses'])
        entities = MyEntity.objects.filter(id__in=entity_ids, activation_status__in=activation_statuses)
        serializer = self.serializer_class(entities, many=True)
        
        # Adding Employees for entity
        entity_id_wise_employees = get_entity_id_wise_employees(entity_ids)
        for entity in serializer.data:
            entity["employees"] = entity_id_wise_employees[entity["id"]]
        add_address_details_to_entities(serializer.data)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class CountOfEntitiesAndProducts(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee,)

    def get(self, request, *args, **kwargs):
        entity_ids = entity_ids_for_user(request.user.id)
        active_entity_ids = MyEntity.objects.active().filter(id__in=entity_ids)

        entities_count = len(active_entity_ids)
        total_products_in_entities = get_total_products_count_in_entities(entity_ids)
        return Response(
            {
                'entities_count': entities_count,
                'products_count': total_products_in_entities
            }, 200)


class BusinessClientEntitiesByType(generics.RetrieveAPIView):
    serializer_class = EntitySerializer
    queryset = BusinessClientEntity.objects.all()
    permission_classes = (IsAuthenticated, IsBusinessClient | IsEmployee)

    def get(self, request, *args, **kwargs):
        entity_ids = entity_ids_for_user(request.user.id)
        data = defaultdict(list)
        for each_category in EntityTypes:
            data[each_category.value] = []
        entity_details = MyEntity.objects.active().filter(id__in=entity_ids)
        all_entities = []

        for each_entity in entity_details:
            all_entities.append(each_entity.id)
            data[each_entity.type].append({each_entity.id: each_entity.name})

        data["ALL"] = all_entities
        return Response(data, status=status.HTTP_200_OK)


class EntityRegistrationDetail(generics.UpdateAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,
        IsBusinessClientEntity | IsEmployeeEntity)
    serializer_class = EntityRegistrationSerializer
    queryset = EntityRegistration.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(registration=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Registration Details",
                             "errors": "Invalid Registration Id"}, status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, entity)
        return super().put(request, *args, **kwargs)


class EntityAccountDetail(generics.UpdateAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,
        IsBusinessClientEntity | IsEmployeeEntity)
    serializer_class = EntityAccountSerializer
    queryset = EntityAccount.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(account=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Account Details",
                             "errors": "Invalid Account Id"}, status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, entity)
        return super().put(request, *args, **kwargs)


class EntityUPIDetail(generics.UpdateAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,
        IsBusinessClientEntity | IsEmployeeEntity)
    serializer_class = EntityUPISerializer
    queryset = EntityUPI.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(upi=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Account Details",
                             "errors": "Invalid UPI Id"}, status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, entity)
        return super().put(request, *args, **kwargs)


class EntityBasicDetail(generics.UpdateAPIView):
    permission_classes = (
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,
        IsBusinessClientEntity | IsEmployeeEntity)
    serializer_class = EntitySerializer
    queryset = MyEntity.objects.all()

    def put(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"message": "Can't update Basic Details",
                             "errors": "Invalid Outlet Id"}, status=status.HTTP_400_BAD_REQUEST)

        self.check_object_permissions(request, entity)
        return super().put(request, *args, **kwargs)
