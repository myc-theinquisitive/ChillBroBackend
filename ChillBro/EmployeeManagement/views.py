from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from collections import deque, defaultdict
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from ChillBro.permissions import IsSuperAdminOrMYCEmployee
from .wrappers import get_employee_details


def get_employee_details_with_manager(employee_ids):
    employee_manager_ids = MYCEmployee.objects.filter(employee__in=employee_ids).values_list('reporting_manager',
                                                                                             'employee')
    manager_ids = list(map(lambda x: x[0], employee_manager_ids))
    employees = get_employee_details(employee_ids + list(manager_ids))
    employees_data = {}
    for employee_manager in employee_manager_ids:
        manager_id, employee_id = employee_manager
        employees_data[employee_id] = employees[employee_id]
        employees_data[employee_id]['manager name'] = employees[manager_id]['first_name']
    return employees_data


def get_department_wise_employeeids(department):
    return MYCEmployee.objects.filter(department=department).values_list('employee')


def get_department_wise_employee_details(department):
    employee_ids = get_department_wise_employeeids(department)
    return get_employee_details_with_manager(employee_ids)


def get_manager_wise_employeeids(manager):
    return MYCEmployee.objects.filter(reporting_manager=manager).values_list('employee')


def get_manager_wise_employee_details(manager):
    employee_ids = get_manager_wise_employeeids(manager)
    return get_employee_details(employee_ids)


def get_manager_wise_all_levels_employee_details(manager):
    employee_ids = MYCEmployee.objects.filter(reporting_manager=manager).values_list('employee', flat=True)
    if len(employee_ids) == 0:
        return []
    q = deque(employee_ids)
    visited = defaultdict(int)
    final_employee_ids = employee_ids[:]
    for employee_id in employee_ids:
        visited[employee_id] = 0
    visited[q[0]] = 1
    while len(q) != 0:
        manager = q.popleft()
        employee_ids = MYCEmployee.objects.filter(reporting_manager=manager).values_list('employee', flat=True)
        for employee_id in employee_ids:
            if visited[employee_id] == 0:
                q.append(employee_id)
                visited[employee_id] = 1
                final_employee_ids.append(employee_id)
    return get_employee_details_with_manager(final_employee_ids)


class MYCEmployeeList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = MYCEmployee.objects.all()
    serializer_class = MYCEmployeeSerializer


class MYCEmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = MYCEmployee.objects.all()
    serializer_class = MYCEmployeeSerializer


class IdProofsList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = IdProofs.objects.all()
    serializer_class = IdProofsSerializer


class IdProofsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = IdProofs.objects.all()
    serializer_class = IdProofsSerializer


class SalaryAccountList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = SalaryAccount.objects.all()
    serializer_class = SalaryAccountSerializer


class SalaryAccountDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = SalaryAccount.objects.all()
    serializer_class = SalaryAccountSerializer


class EmployeeFullDetails(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        try:
            myc_employee = MYCEmployee.objects.get(employee=kwargs['employee_id'])
            id_proofs = IdProofs.objects.filter(employee=kwargs['employee_id'])
            salary_account = SalaryAccount.objects.get(employee=kwargs['employee_id'])
        except Exception as e:
            print(e)
            return Response({"Error": "Does not exist", "message": "Employee id not found "})

        myc_employee_serializer = MYCEmployeeSerializer(myc_employee)
        id_proofs_serializer = IdProofsSerializer(id_proofs, many=True)
        salary_account_serializer = SalaryAccountSerializer(salary_account)

        employee_data = get_employee_details([kwargs['employee_id']])[0]
        employee_data['myc_employee'] = myc_employee_serializer.data
        employee_data['id_proofs'] = id_proofs_serializer.data
        employee_data['salary_account'] = salary_account_serializer.data

        return Response(employee_data)


class DepartmentWiseEmployee(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        department = kwargs['department']
        department_employees = get_department_wise_employee_details(department)
        return Response(department_employees)


class ManagerWiseEmployee(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        manager = kwargs['manager']
        manager_employees = get_manager_wise_employee_details(manager)
        return Response(manager_employees)


class ManagerWiseAllLevelEmployee(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        manager = kwargs['manager']
        manager_employees = get_manager_wise_all_levels_employee_details(manager)
        return Response(manager_employees)


class AttendanceList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get(self, request, *args, **kwargs):
        if "date" not in request.data:
            return Response({"message": "Date is required field"}, 400)
        date = request.data["date"]
        employee_ids = []
        if "department" in request.data:
            department = request.data["department"]
            employee_ids = get_department_wise_employeeids(department)
        elif "manager" in request.data:
            manager = request.data["manager"]
            employee_ids = get_manager_wise_employeeids(manager)

        self.queryset = Attendance.objects.filter(employee__in=employee_ids, date=date)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        attendances = request.data['attendances']
        attendance_serializer = self.serializer_class(data=attendances, many=True)
        if attendance_serializer.is_valid():
            self.serializer_class.bulk_create(attendances)
            return Response({"message": "Attendance updated successfully"}, 200)
        return Response(attendance_serializer.errors, 400)


class AttendanceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee)
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer


class LeavesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Leaves.objects.all()
    serializer_class = LeavesSerializer

    def post(self, request, *args, **kwargs):
        request.data['employee'] = request.user.id
        super().post(self, request, *args, **kwargs)


class LeavesDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Leaves.objects.all()
    serializer_class = LeavesSerializer


class PendingLeavesList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Leaves.objects.all()
    serializer_class = LeavesSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Leaves.objects.filter(approval_status="PENDING")
        super().get(request, *args, **kwargs)

