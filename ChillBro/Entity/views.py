from django.db.models import Count
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer, AddressSerializer
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .wrappers import post_create_address, get_total_products_count_in_entities
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, IsEmployee, IsGet, IsEmployeeEntity


class EntityList(generics.CreateAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated, IsBusinessClient,)

    def post(self, request, *args, **kwargs):
        if 'city' not in request.data or 'pincode' not in request.data:
            return Response({"message": "City and Pincode are required"}, status=status.HTTP_400_BAD_REQUEST)
        response_from_address = post_create_address(request.data['city'], request.data['pincode'])
        if response_from_address['is_valid']:
            request.data._mutable = True
            request.data['address_id'] = response_from_address["address_id"]
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                entity_id = serializer.data['id']
                request.data['entity_id'] = entity_id
                request.data['business_client_id'] = request.user.id
                business_client_entity_serializer = BusinessClientEntitySerializer(data=request.data)
                if business_client_entity_serializer.is_valid():
                    business_client_entity_serializer.save()
                    return Response({"message": "success"}, status=status.HTTP_200_OK)
                else:
                    instance.delete()
                    return Response(business_client_entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "City or Pincode is invalid","errors":response_from_address["errors"]},
                            status=status.HTTP_400_BAD_REQUEST)


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient | (IsEmployee & IsGet), IsBusinessClientEntity)

    def check_entity_permission(self, request):
        try:
            entity = MyEntity.objects.get(id=self.kwargs['pk'])
            self.check_object_permissions(request, entity)
        except:
            pass

    def get(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        super().post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.check_entity_permission(request)
        super().put(request, *args, **kwargs)

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
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsBusinessClientEntity | IsEmployeeEntity)

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


class CountOfEntitiesAndProducts(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        business_client_entities = BusinessClientEntity.objects.filter(business_client_id=request.user) \
                                    .values_list('entity_id', flat=True)
        business_client_entities_count = business_client_entities.aggregate(count=Count('entity_id'))['count']
        total_products_in_entities = get_total_products_count_in_entities(business_client_entities)
        return Response({'entities_count':business_client_entities_count,\
                         'products_count': total_products_in_entities},200)




