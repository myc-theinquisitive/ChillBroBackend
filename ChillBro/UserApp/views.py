from .models import *
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .wrapper import get_entity_ids_for_business_client


# Create your views here.

class MyUserList(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer


class BusinessClientAdd(APIView):
    queryset = BusinessClient.objects.all()
    serializer_class = NewBusinessClientSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data._mutable = True
            request.data['is_verified'] = True
            user_serializer = MyUserList.serializer_class(data=request.data)
            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                user_id = user_serializer.data['id']
                request.data['user_id'] = user_id
                business_client_serializer = BusinessClientSerializer(data=request.data)
                if business_client_serializer.is_valid():
                    business_client_serializer.save()
                    return Response({'message': 'Success'}, status=status.HTTP_200_OK)
                else:
                    user_instance.delete()
                    return Response(business_client_serializer.errors)
            else:
                return Response(user_serializer.errors)
        else:
            return Response(serializer.errors)


class BusinessClientAll(generics.ListCreateAPIView):
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer


class BusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer

    def get(self, request, *args, **kwargs):
        try:
            business_client = BusinessClient.objects.filter(id=self.kwargs['pk']). \
                values('user_id__first_name', 'user_id__email', 'user_id__phone_number', 'business_name',
                       'secondary_contact')[0]
            return Response(business_client)
        except:
            return Response({"message": "Detail not found"})


class EmployeeAdd(APIView):
    queryset = Employee.objects.all()
    serializer_class = NewEmployeeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data['is_verified'] = True
            user_serializer = MyUserList.serializer_class(data=request.data)
            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                user_id = user_serializer.data['id']
                request.data['user_id'] = user_id
                employee_serializer = EmployeeSerializer(data=request.data)
                if employee_serializer.is_valid():
                    employee_serializer.save()
                    return Response({'message': 'Success'}, status=status.HTTP_200_OK)
                else:
                    user_instance.delete()
                    return Response(employee_serializer.errors)
            else:
                return Response(user_serializer.errors)
        else:
            return Response(serializer.errors)


class EmployeeAll(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        business_client = Employee.objects.filter(id=self.kwargs['pk']). \
            values('user_id__first_name', 'user_id__email', 'user_id__phone_number', 'entity', 'role', 'is_active', 'image')[0]
        return Response(business_client)


class EntityBusinessClientEmployee(generics.ListAPIView):
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer

    def get(self, request, *args, **kwargs):
        entity_ids = get_entity_ids_for_business_client(self.kwargs['bc_id'])
        employees = Employee.objects.filter(entity_id__in=entity_ids)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class EmployeeActive(generics.RetrieveUpdateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeActiveSerializer