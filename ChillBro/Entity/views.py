from django.shortcuts import render
from .serializers import EntitySerializer, EntityStatusSerializer, BusinessClientEntitySerializer
from rest_framework import generics
from .models import MyEntity, BusinessClientEntity
from rest_framework.response import Response
from rest_framework import status
from django.http import  HttpResponse
from .constants import SHARE_APP_MESSAGE

class EntityList(generics.ListCreateAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer


class EntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MyEntity.objects.all()
    serializer_class = EntitySerializer

class EntityStatusAll(generics.GenericAPIView):
    serializer_class = EntityStatusSerializer

    def put(self,request):
        serializer =self.serializer_class(data=request.data)
        if serializer.is_valid():
            queryset = MyEntity.objects.all()
            queryset.update(status=serializer.data['status'])
            return Response({"Message":"Success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EntityStatus(generics.GenericAPIView):
    serializer_class = EntityStatusSerializer

    def put(self, request,pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            queryset = MyEntity.objects.get(id=pk)
            queryset.status=serializer.data['status']
            queryset.save()
            return Response({"Message": "Success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusinessClientEntityList(generics.CreateAPIView):
    queryset = BusinessClientEntity.objects.all()
    serializer_class = BusinessClientEntitySerializer

class BusinessClientEntityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessClientEntity.objects.all()
    serializer_class = BusinessClientEntitySerializer

class BusinessClientOutlets(generics.ListAPIView):
    serializer_class = EntitySerializer

    def get_queryset(self):
        queryset = BusinessClientEntity.objects.filter(business_client_id=self.kwargs['bc_id'])
        return queryset

    def get(self,request,bc_id):
        entity_ids=self.get_queryset().values_list('entity_id',flat=True)
        entities=MyEntity.objects.filter(id__in=entity_ids)
        serializer=self.serializer_class(entities,many=True)
        return Response(serializer.data)

def ShareApp(request):
    return HttpResponse(SHARE_APP_MESSAGE)

def get_entity_ids(business_client_id):
    entity_ids=BusinessClientEntity.objects.filter(business_client_id=business_client_id).values_list('entity_id',flat=True)
    return entity_ids