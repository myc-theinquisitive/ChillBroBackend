import json
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, FloatField, DecimalField
from rest_framework.views import APIView
from .constants import ActivationStatus, EntityType
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer, \
    EntityVerificationSerializer, EntityAccountSerializer, EntityUPISerializer, EntityEditSerializer, \
    EntityDetailsSerializer, EntityVerificationUpdateInputSerializer, GetEntitiesByStatusSerializer, \
    EntityRegistrationSerializer, GetEntitiesBySearchFilters, AmenitiesSerializer, \
    AmenityIsAvailableSerializer, EntityAvailableAmenitiesSerializer, NewEntitySerializer, \
    EntityAvailableAmenitiesUpdateSerializer, EntityImageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity, EntityVerification, EntityUPI, EntityAccount, \
    EntityRegistration, Amenities, EntityAvailableAmenities, EntityImage
from rest_framework.response import Response
from rest_framework import status
from .wrappers import post_create_address, get_address_details_for_address_ids, get_total_products_count_in_entities, \
    update_address_for_address_id, get_entity_id_wise_employees, get_entity_ids_for_employee, \
    get_entity_id_wise_average_rating, average_rating_query_for_entity, entity_products_starting_price_query, \
    get_entity_id_wise_starting_price, get_entity_id_wise_wishlist_status, get_rating_wise_review_details_for_entity, \
    get_rating_type_wise_average_rating_for_entity, get_latest_ratings_for_entity, \
    approximate_distance_query_for_entity
from datetime import datetime
from .helpers import get_date_format, get_entity_status, get_entity_types_filter, LatLong, \
    calculate_distance_between_multiple_points
from collections import defaultdict
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, \
    IsEmployee, IsGet, IsEmployeeEntity
from decimal import Decimal
from django.conf import settings

from collections import defaultdict


def filter_entity_ids_by_city(entity_ids, city):
    from .wrappers import filter_address_ids_by_city
    address_ids = MyEntity.objects.filter(id__in=entity_ids).values_list("address_id", flat=True)
    city_address_ids = filter_address_ids_by_city(address_ids, city)
    return MyEntity.objects.filter(id__in=entity_ids, address_id__in=city_address_ids) \
        .values_list("id", flat=True)


def entity_ids_for_user(user_id):
    entity_ids = BusinessClientEntity.objects.filter(
        business_client_id=user_id).values_list('entity_id', flat=True)
    if len(entity_ids) == 0:
        entity_ids = get_entity_ids_for_employee(user_id)
    return entity_ids


def get_entity_details(entity_ids):
    entities_data = MyEntity.objects.filter(id__in=entity_ids) \
        .values('id', 'name', 'type', 'sub_type', 'address_id')
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


def validate_amenity_ids(amenity_ids):
    existing_amenities = Amenities.objects.filter(id__in=amenity_ids).values_list('id', flat=True)
    if len(existing_amenities) != len(amenity_ids):
        return False, set(amenity_ids) - set(existing_amenities)
    return True, []


def validate_entity_available_amenities_ids(entity_id, entity_available_amenity_ids):
    existing_entity_available_amenity_ids \
        = EntityAvailableAmenities.objects.filter(id__in=entity_available_amenity_ids, entity_id=entity_id) \
        .values_list('id', flat=True)
    if len(existing_entity_available_amenity_ids) != len(entity_available_amenity_ids):
        return False, set(entity_available_amenity_ids) - set(existing_entity_available_amenity_ids)
    return True, []


class EntityImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsEmployeeEntity | IsBusinessClientEntity)
    queryset = EntityImage.objects.all()
    serializer_class = EntityImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            entity = MyEntity.objects.get(id=request.data['entity'])
        except ObjectDoesNotExist:
            return Response({"errors": "Entity does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request, entity)

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity_image = EntityImage.objects.get(entity=entity, order=request.data["order"])
            return Response({"errors": "Image with order already Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass

        serializer.create(request.data)
        return Response({"message": "Entity Image added successfully"}, status=status.HTTP_201_CREATED)


class EntityImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsEmployeeEntity | IsBusinessClientEntity)
    queryset = EntityImage.objects.all()
    serializer_class = EntityImageSerializer

    def delete(self, request, *args, **kwargs):
        try:
            entity_image = EntityImage.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return Response({"errors": "Entity image does not Exist!!!"}, status=status.HTTP_400_BAD_REQUEST)
        self.check_object_permissions(request, entity_image.entity)

        return super().delete(request, *args, **kwargs)


class EntityList(generics.ListCreateAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated & (IsSuperAdminOrMYCEmployee | IsBusinessClient),)

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        add_verification_details_to_entities(response.data["results"])
        add_address_details_to_entities(response.data["results"])
        return response

    @staticmethod
    def validate_entity_amenities(amenities_data):
        errors = defaultdict(list)
        is_valid = True

        serializer = AmenityIsAvailableSerializer(data=amenities_data, many=True)
        if not serializer.is_valid():
            return False, serializer.errors

        amenity_ids = []
        for amenity_dict in amenities_data:
            amenity_ids.append(amenity_dict["amenity"])

        amenity_ids_valid, invalid_ids = validate_amenity_ids(amenity_ids)
        if not amenity_ids_valid:
            is_valid = False
            errors["invalid_amenity_ids"] = invalid_ids

        return is_valid, errors

    def post(self, request, *args, **kwargs):
        request_data = request.data.dict()
        address_data = request_data.pop('address', {})
        # remove while not using forms from postman
        address_data = json.loads(address_data)

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

        amenities_data = request_data.pop("amenities", [])
        # remove while not using forms from postman
        amenities_data = json.loads(amenities_data)
        amenities_data_valid, errors = self.validate_entity_amenities(amenities_data)
        if not amenities_data_valid:
            return Response({"message": "Can't create outlet", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validating images
        entity_images = request_data.pop("images", [])
        entity_image_serializer = EntityImageSerializer(data=entity_images, many=True)
        if not entity_image_serializer.is_valid():
            Response({"message": "Can't create outlet", "errors": entity_image_serializer.errors},
                     status=status.HTTP_400_BAD_REQUEST)

        request.data._mutable = True
        serializer = NewEntitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"message": "Can't create outlet", "errors": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        address_details = post_create_address(address_data)
        if not address_details['is_valid']:
            return Response({"message": "Can't create outlet", "errors": address_details['errors']},
                            status=status.HTTP_400_BAD_REQUEST)

        registration_instance = entity_registration_serializer.save()
        upi_instance = entity_upi_serializer.save()
        account_instance = entity_account_serializer.save()

        request.data['address_id'] = address_details['address_id']
        request.data['registration'] = registration_instance.id
        request.data['account'] = account_instance.id
        request.data['upi'] = upi_instance.id
        entity = EntitySerializer().create(request.data)

        for amenity in amenities_data:
            amenity["entity"] = entity.id
        entity_available_amenities_serializer = EntityAvailableAmenitiesSerializer()
        entity_available_amenities_serializer.bulk_create(amenities_data)

        entity_image_dicts = []
        for image_dict in entity_images:
            entity_image_dict = {
                "entity": entity.id,
                "image": image_dict["image"],
                "order": image_dict["order"]
            }
            entity_image_dicts.append(entity_image_dict)
        EntityImageSerializer.bulk_create(entity_image_dicts)

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
        IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntity | IsEmployeeEntity | IsGet)

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

    @staticmethod
    def validate_entity_amenities(entity_id, amenities_data):
        is_valid = True
        errors = defaultdict(list)

        entity_available_amenities_update_serializer = EntityAvailableAmenitiesUpdateSerializer(data=amenities_data)
        entity_available_amenities_update_data_valid = entity_available_amenities_update_serializer.is_valid()

        if not entity_available_amenities_update_data_valid:
            is_valid = False
            errors.update(entity_available_amenities_update_serializer.errors)
            return is_valid, errors

        # Additional validations except serializer validations
        amenity_ids = []
        entity_available_amenity_ids = []
        for amenity in amenities_data["add"]:
            entity_available_amenities_exists = EntityAvailableAmenities.objects \
                .filter(entity_id=entity_id, amenity_id=amenity["amenity"]).exists()
            if entity_available_amenities_exists:
                is_valid = False
                errors["Entity-Amenity"].append("Entity-{0}, Amenity-{1}: Already Exists!"
                                                .format(entity_id, amenity["amenity"]))

            amenity["entity"] = entity_id
            amenity_ids.append(amenity["amenity"])

        for amenity in amenities_data["change"]:
            entity_available_amenity_ids.append(amenity["id"])

        for amenity in amenities_data["delete"]:
            entity_available_amenity_ids.append(amenity["id"])

        amenity_ids_valid, invalid_amenity_ids = validate_amenity_ids(amenity_ids)
        if not amenity_ids_valid:
            is_valid = False
            errors["invalid_amenity_ids"] = invalid_amenity_ids

        entity_available_amenities_ids_valid, invalid_entity_available_amenities_ids \
            = validate_entity_available_amenities_ids(entity_id, entity_available_amenity_ids)
        if not entity_available_amenities_ids_valid:
            is_valid = False
            errors["invalid_entity_available_amenities_ids"] = invalid_entity_available_amenities_ids

        return is_valid, errors

    def put(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        entity = MyEntity.objects.get(id=self.kwargs['pk'])
        if entity.activation_status == ActivationStatus.DELETED.value:
            return Response({"message": "Can't update outlet details",
                             "errors": "Entity is already deleted"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EntityEditSerializer(entity, data=request.data)

        address_data = request.data.dict().pop("address", {})
        # remove while not using forms from postman
        address_data = json.loads(address_data)
        address_id = entity.address_id

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

        request_data = request.data.dict()
        amenities_data = request_data.pop("amenities", {"add": [], "change": [], "delete": []})
        # remove while not using forms from postman
        amenities_data = json.loads(amenities_data)
        amenities_data_valid, errors = self.validate_entity_amenities(entity.id, amenities_data)
        if not amenities_data_valid:
            return Response({"message": "Can't update outlet details", "errors": errors},
                            status=status.HTTP_400_BAD_REQUEST)

        address_details = update_address_for_address_id(address_id, address_data)
        if not address_details['is_valid']:
            return Response({"message": "Can't update outlet details", "errors": address_details['errors']},
                            status=status.HTTP_400_BAD_REQUEST)

        entity_available_amenities_serializer = EntityAvailableAmenitiesSerializer()
        entity_available_amenities_serializer.bulk_create(amenities_data["add"])
        entity_available_amenities_serializer.bulk_update(amenities_data["change"])
        entity_available_amenities_serializer.bulk_delete(amenities_data["delete"])

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

        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class BusinessClientEntitiesByVerificationStatus(generics.ListAPIView):
    serializer_class = EntitySerializer
    queryset = MyEntity.objects.all()
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | IsEmployee,)

    def post(self, request, *args, **kwargs):
        input_serializer = GetEntitiesByStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get entities", "errors": input_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        entity_ids = entity_ids_for_user(request.user.id)
        entity_types = get_entity_types_filter(request.data['entity_types'])
        activation_statuses = get_entity_status(request.data['statuses'])
        entities = MyEntity.objects.filter(
            id__in=entity_ids, type__in=entity_types, activation_status__in=activation_statuses)
        serializer = self.serializer_class(entities, many=True)

        entity_ids = []
        for entity in entities:
            entity_ids.append(entity.id)

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
        for each_category in EntityType:
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


class AmenitiesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet)
    queryset = Amenities.objects.all()
    serializer_class = AmenitiesSerializer


def convert_available_amenities_to_dict(available_amenity):
    image_url = available_amenity.amenity.icon_url.url
    image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
    return {
        "name": available_amenity.amenity.name,
        "icon_url": image_url,
        "is_available": available_amenity.is_available
    }


def get_entity_id_wise_amenities_dict(entity_ids):
    entity_amenities = EntityAvailableAmenities.objects.select_related('amenity').filter(entity_id__in=entity_ids)
    entity_id_wise_amenities_dict = defaultdict(list)
    for available_amenity in entity_amenities:
        entity_id = available_amenity.entity_id
        entity_id_wise_amenities_dict[entity_id].append(
            convert_available_amenities_to_dict(available_amenity)
        )
    return entity_id_wise_amenities_dict


def get_entity_id_wise_images(entity_ids):
    entity_images = EntityImage.objects.filter(entity_id__in=entity_ids)

    entity_id_wise_images_dict = defaultdict(list)
    for entity_image in entity_images:
        image_url = entity_image.image.url
        image_url = image_url.replace(settings.IMAGE_REPLACED_STRING, "")
        entity_id_wise_images_dict[entity_image.entity_id].append(image_url)

    return entity_id_wise_images_dict


class EntityView:

    @staticmethod
    def add_average_rating_for_entities(entities_response):
        entity_ids = []
        for entity in entities_response:
            entity_ids.append(entity["id"])

        entity_id_wise_rating = get_entity_id_wise_average_rating(entity_ids)
        for entity in entities_response:
            entity["rating"] = entity_id_wise_rating[entity["id"]]

    @staticmethod
    def add_starting_price_for_entities(entities_response):
        entity_ids = []
        for entity in entities_response:
            entity_ids.append(entity["id"])

        entity_id_wise_starting_price = get_entity_id_wise_starting_price(entity_ids)
        for entity in entities_response:
            entity["starting_price"] = entity_id_wise_starting_price[entity["id"]]

    @staticmethod
    def add_wishlist_status_for_entities(user_id, entities_response):
        entity_ids = []
        for entity in entities_response:
            entity_ids.append(entity["id"])

        entity_id_wise_wishlist_status = get_entity_id_wise_wishlist_status(user_id, entity_ids)
        for entity in entities_response:
            entity["in_wishlist"] = entity_id_wise_wishlist_status[entity["id"]]

    @staticmethod
    def add_amenities_for_entities(entities_response):
        entity_ids = []
        for entity in entities_response:
            entity_ids.append(entity["id"])

        entity_id_wise_amenities_dict = get_entity_id_wise_amenities_dict(entity_ids)
        for entity in entities_response:
            entity["amenities"] = entity_id_wise_amenities_dict[entity["id"]]

    @staticmethod
    def add_images_for_entities(entities_response):
        entity_ids = []
        for entity in entities_response:
            entity_ids.append(entity["id"])

        entity_id_wise_images_dict = get_entity_id_wise_images(entity_ids)
        for entity in entities_response:
            entity["images"] = entity_id_wise_images_dict[entity["id"]]

    @staticmethod
    def update_entities_response(entity_response):
        entity_response.pop("status", None)
        entity_response.pop("active_from", None)
        entity_response.pop("activation_status", None)
        entity_response.pop("created_at", None)
        entity_response.pop("registration", None)
        entity_response.pop("account", None)
        entity_response.pop("upi", None)

    @staticmethod
    def add_distance_data_for_entities(entities_response, request_data):
        if "location" not in request_data or request_data["location"] is None:
            for entity in entities_response:
                entity["distance"] = ""
                entity["duration"] = ""
            return None

        location = request_data["location"]
        if "longitude" not in location or "latitude" not in location:
            for entity in entities_response:
                entity["distance"] = ""
                entity["duration"] = ""
            return None

        source = LatLong(location["latitude"], location["longitude"])

        destination_points = []
        for entity in entities_response:
            address = entity['address']
            destination_points.append((entity['id'], LatLong(address['latitude'], address['longitude'])))

        distances_data = calculate_distance_between_multiple_points(source, destination_points)

        for entity in entities_response:
            distance_data = distances_data[entity['id']]
            entity['distance'] = distance_data['distance']
            entity['duration'] = distance_data['duration']

    def add_details_for_entities(self, entities_data):
        self.add_average_rating_for_entities(entities_data)
        self.add_starting_price_for_entities(entities_data)
        self.add_amenities_for_entities(entities_data)
        self.add_images_for_entities(entities_data)
        add_address_details_to_entities(entities_data)
        for entity_response in entities_data:
            self.update_entities_response(entity_response)

    def add_user_specific_details_for_entities(self, user_id, entities_data):
        self.add_wishlist_status_for_entities(user_id, entities_data)

    def get_by_ids(self, entity_ids):
        entities = MyEntity.objects.filter(id__in=entity_ids)
        entities_data = EntitySerializer(entities, many=True).data
        self.add_details_for_entities(entities_data)
        return entities_data

    def get_by_id(self, entity_id):
        entity = MyEntity.objects.get(id=entity_id)
        entity_data = EntitySerializer(entity).data

        self.update_entities_response(entity_data)
        self.add_starting_price_for_entities([entity_data])
        self.add_amenities_for_entities([entity_data])
        self.add_images_for_entities([entity_data])
        add_address_details_to_entities([entity_data])

        return entity_data


class GetEntitiesDetailsForUser(APIView):
    permission_classes = (IsAuthenticated,)
    entity_view = EntityView()

    def get(self, request, *args, **kwargs):
        entity_id = kwargs['pk']
        try:
            entity_data = self.entity_view.get_by_id(entity_id)
        except ObjectDoesNotExist:
            return Response({"message": "Can't get entity details", "errors": "Invalid Entity Id"},
                            status=status.HTTP_200_OK)

        self.entity_view.add_user_specific_details_for_entities(request.user, [entity_data])
        rating_stats = get_rating_wise_review_details_for_entity(entity_id)
        rating_type_stats = get_rating_type_wise_average_rating_for_entity(entity_id)
        reviews_list = get_latest_ratings_for_entity(entity_id)
        entity_data["reviews"] = {
            "rating_stats": rating_stats,
            "rating_type_stats": rating_type_stats,
            "review_list": reviews_list
        }
        return Response(entity_data, status=status.HTTP_200_OK)


class GetEntitiesBySubType(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EntitySerializer
    entity_view = EntityView()

    @staticmethod
    def apply_filters(entity_ids, filter_data):
        # applying search filter
        if filter_data["search_text"]:
            filter_entities = MyEntity.objects.search(filter_data["search_text"]).filter(id__in=entity_ids)
        else:
            filter_entities = MyEntity.objects.filter(id__in=entity_ids)

        # applying location Filters
        location_filter = filter_data["location_filter"]
        if location_filter["applied"]:
            entity_ids = filter_entities.values_list("id", flat=True)
            city_entity_ids = filter_entity_ids_by_city(entity_ids, location_filter["city"])
            filter_entities = filter_entities.filter(id__in=city_entity_ids)

        return filter_entities.values_list("id", flat=True)

    @staticmethod
    def apply_sort_filter(query_set, sort_filter, request_data):
        if sort_filter == "AVERAGE_RATING":
            ratings_query = average_rating_query_for_entity(OuterRef('id'))
            return query_set.annotate(
                average_rating=Subquery(
                    queryset=ratings_query,
                    output_field=FloatField()
                )
            ).order_by('-average_rating')

        elif sort_filter == "PRICE_LOW_TO_HIGH" or sort_filter == "PRICE_HIGH_TO_LOW":
            starting_price_query = entity_products_starting_price_query(OuterRef('id'))
            query_set = query_set.annotate(
                starting_price=Subquery(
                    queryset=starting_price_query,
                    output_field=DecimalField()
                )
            )
            if sort_filter == "PRICE_LOW_TO_HIGH":
                return query_set.order_by('starting_price')
            elif sort_filter == "PRICE_HIGH_TO_LOW":
                return query_set.order_by('-starting_price')

        elif sort_filter == "DISTANCE":
            if "location" in request_data and request_data["location"] is not None:
                latitude = request_data["location"]["latitude"]
                longitude = request_data["location"]["longitude"]
                distance_query = approximate_distance_query_for_entity(
                    OuterRef('address_id'), latitude, longitude)
                return query_set.annotate(
                    approximate_distance=Subquery(
                        queryset=distance_query,
                        output_field=FloatField()
                    )
                ).order_by('approximate_distance')

        return query_set

    @staticmethod
    def sort_results(entities_response, sort_filter):
        if sort_filter == "AVERAGE_RATING":
            entities_response.sort(
                key=lambda entity_response: Decimal(entity_response['rating']['avg_rating']), reverse=True)
        elif sort_filter == "PRICE_LOW_TO_HIGH":
            entities_response.sort(key=lambda entity_response: Decimal(entity_response['starting_price']))
        elif sort_filter == "PRICE_HIGH_TO_LOW":
            entities_response.sort(
                key=lambda entity_response: Decimal(entity_response['starting_price']), reverse=True)
        elif sort_filter == "DISTANCE":
            entities_response.sort(
                key=lambda entity_response: entity_response['distance'])

    def post(self, request, *args, **kwargs):

        input_serializer = GetEntitiesBySearchFilters(data=request.data)
        if not input_serializer.is_valid():
            return Response({"message": "Can't get outlets", "errors": input_serializer.errors}, 400)

        entity_ids = MyEntity.objects.filter(sub_type__icontains=kwargs["slug"]).values_list("id", flat=True)
        sort_filter = request.data["sort_filter"]
        entity_ids = self.apply_filters(entity_ids, request.data)
        self.queryset = MyEntity.objects.filter(id__in=entity_ids)
        self.queryset = self.apply_sort_filter(self.queryset, sort_filter, request.data)

        response = super().get(request, args, kwargs)
        response_data = response.data["results"]
        self.entity_view.add_details_for_entities(response_data)
        self.entity_view.add_distance_data_for_entities(response_data, request.data)
        self.entity_view.add_user_specific_details_for_entities(request.user.id, response_data)
        self.sort_results(response_data, sort_filter)
        return response


class HotelHomePageCategories(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EntitySerializer
    entity_view = EntityView()

    def get(self, request, *args, **kwargs):

        entity_ids = MyEntity.objects.filter(sub_type__icontains="hotel").values_list("id", flat=True)

        entities = MyEntity.objects.filter(id__in=entity_ids)
        entity_serializer = EntitySerializer(entities, many=True)

        response_data = entity_serializer.data
        self.entity_view.add_details_for_entities(response_data)
        self.entity_view.add_user_specific_details_for_entities(request.user.id, response_data)

        hotel_categories_home_page = defaultdict(list)

        count = 0
        for each_product in range(len(response_data)):
            if count % 3 == 0:
                hotel_categories_home_page['Near By You'].append(response_data[count])
            if count % 3 == 1:
                hotel_categories_home_page["Trending"].append(response_data[count])
            if count % 3 == 2:
                hotel_categories_home_page['Budget'].append(response_data[count])
            hotel_categories_home_page['All Hotels'].append(response_data[count])
            count += 1

        hotel_home_page_categories = [
            {
                'name': 'Near By You',
                'products': hotel_categories_home_page['Near By You']
            },
            {
                'name': "Trending",
                'products': hotel_categories_home_page["Trending"]
            },
            {
                'name': 'Budget',
                'products': hotel_categories_home_page['Budget']
            },
            {
                'name': 'All Hotels',
                'products': hotel_categories_home_page['All Hotels']
            }
        ]

        return Response({"results": hotel_home_page_categories}, 200)
