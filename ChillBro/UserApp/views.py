from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .wrapper import get_entity_ids_for_business_client
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsBusinessClient, IsBusinessClientEntity, IsOwnerById, \
    IsEmployee, IsEmployeeEntityById, IsBusinessClientEmployee, IsOwnerById, IsEmployeeBusinessClient


class MyUserList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer


class BusinessClientAdd(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee,)
    queryset = BusinessClient.objects.all()
    serializer_class = NewBusinessClientSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data['is_verified'] = True
            request.data['email'] = request.data['email'].lower().strip()
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
                    return Response(business_client_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response(user_serializer.errors,400)
        else:
            return Response(serializer.errors,400)


class BusinessClientAll(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee,)
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer


class BusinessClientDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsOwnerById)
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['pk'])
        business_client = BusinessClient.objects.filter(user_id=self.kwargs['pk']). \
            values('business_name', 'secondary_contact', first_name=F('user_id__first_name'),
                   email=F('user_id__email'), phone_number=F('user_id__phone_number'))[0]
        return Response(business_client)


class EmployeeAdd(APIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClientEntity)
    queryset = Employee.objects.all()
    serializer_class = NewEmployeeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            request.data['is_verified'] = True
            request.data['email'] = request.data['email'].lower().strip()
            user_serializer = MyUserList.serializer_class(data=request.data)
            if user_serializer.is_valid():
                user_instance = user_serializer.save()
                user_instance.set_password(request.data['password'])
                user_instance.save()
                user_id = user_serializer.data['id']
                request.data['user_id'] = user_id

                employee_serializer = EmployeeSerializer(data=request.data)
                if employee_serializer.is_valid():
                    employee_instance = employee_serializer.save()

                    employee_image_dicts = []
                    images = request.data.pop('images', None)
                    for image in images:
                        employee_image_dict = {
                            "employee": employee_instance,
                            "image": image
                        }
                        employee_image_dicts.append(employee_image_dict)

                    EmployeeImageSerializer.bulk_create(employee_image_dicts)
                    return Response({'message': 'Success'}, status=status.HTTP_200_OK)
                else:
                    user_instance.delete()
                    return Response(employee_serializer.errors, 400)
            else:
                return Response(user_serializer.errors, 400)
        else:
            return Response(serializer.errors, 400)


def get_employee_details(employee_ids):
    return Employee.objects.filter(id__in=employee_ids). \
        values('id', 'entity_id', 'role', 'is_active', first_name=F('user_id__first_name'),
               email=F('user_id__email'), phone_number=F('user_id__phone_number'))


def get_employee_details_for_entity_ids(entity_ids):
    return Employee.objects.filter(entity_id__in=entity_ids). \
        values('id', 'entity_id', 'role', 'is_active', first_name=F('user_id__first_name'),
               email=F('user_id__email'), phone_number=F('user_id__phone_number'))


def get_employee_details_with_images(employee_ids):
    employees = get_employee_details(employee_ids)
    for employee in employees:
        employee_images = EmployeeImage.objects.filter(employee=employee['id']).values_list('image', flat=True)
        employee['images'] = employee_images
    return employees


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsEmployeeBusinessClient |
                          (IsEmployee & IsOwnerById))
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['pk'])
        employee = get_employee_details_with_images([kwargs['pk']])[0]
        return Response(employee)

    def put(self, request, *args, **kwargs):
        id = request.user.id
        employee = None
        try:
            employee = Employee.objects.get(user_id=id)
        except ObjectDoesNotExist:
            pass
        if employee:
            request.data['is_active'] = employee.is_active
        return super().put(request, *args, **kwargs)


class EntityBusinessClientEmployee(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient |
                          IsEmployeeBusinessClient,)
    queryset = BusinessClient.objects.all()
    serializer_class = BusinessClientSerializer

    def get(self, request, *args, **kwargs):
        entity_ids = get_entity_ids_for_business_client(request.user.id)
        employee_ids = Employee.objects.filter(entity_id__in=entity_ids).values_list('id')
        employees = get_employee_details_with_images(employee_ids)
        return Response(employees, 200)


class EmployeeActive(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsBusinessClient, IsBusinessClientEmployee)
    queryset = Employee.objects.all()
    serializer_class = EmployeeActiveSerializer

    def get(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['pk'])
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.check_object_permissions(request, kwargs['pk'])
        return super().put(request, *args, **kwargs)


class EmployeeImageCreate(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerById)
    queryset = EmployeeImage.objects.all()
    serializer_class = EmployeeImageSerializer

    def post(self, request, *args, **kwargs):
        employee_id = request.data['employee']
        self.check_object_permissions(request, employee_id)
        super().post(request, *args, **kwargs)


class EmployeeImageDelete(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerById)
    queryset = EmployeeImage.objects.all()
    serializer_class = EmployeeImageSerializer

    def delete(self, request, *args, **kwargs):
        employee_id = request.data['employee']
        self.check_object_permissions(request, employee_id)
        super().delete(request, *args, **kwargs)
