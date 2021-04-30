from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .wrapper import get_entity_ids_for_business_client
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, CheckBusinessClientEntity, IsOwnerById


class MyUserList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer


class BusinessClientAdd(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee, )
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
                user_instance.set_password(request.data['password'])
                user_instance.save()

                request.data['user_id'] = user_instance.id
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
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, )
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer


class BusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,)
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
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | CheckBusinessClientEntity)
    queryset = Employee.objects.all()
    serializer_class = NewEmployeeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data['is_verified'] = True
            user_serializer = MyUserList.serializer_class(data=request.data)
            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                user_instance.set_password(request.data['password'])
                user_instance.save()
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
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, )
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, )
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        business_client = Employee.objects.filter(id=self.kwargs['pk']). \
            values('user_id__first_name', 'user_id__email', 'user_id__phone_number', 'entity_id', 'role', 'is_active',
                   'image')[0]
        return Response(business_client)


class EntityBusinessClientEmployee(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,IsOwnerById,)
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request,self.kwargs['bc_id'])
        entity_ids = get_entity_ids_for_business_client(self.kwargs['bc_id'])
        employees = Employee.objects.filter(entity_id__in=entity_ids)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data,200)


class EmployeeActive(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient,)
    queryset = Employee.objects.all()
    serializer_class = EmployeeActiveSerializer
