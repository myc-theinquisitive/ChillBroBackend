from django.db import models
from .constants import Department, AttendanceStatus, LeaveStatus, LeaveType
import uuid
from django.core.validators import MinLengthValidator
from .validations import validate_ifsc_code, validate_bank_account_no, validate_aadhar, validate_pan
from .helpers import upload_pan_image_for_employee, upload_aadhar_image_for_employee


def get_id():
    return str(uuid.uuid4())


class MYCEmployee(models.Model):
    employee = models.CharField(max_length=36, unique=True, verbose_name="Employee")
    department = models.CharField(
        max_length=50, choices=[(department.value, department.value) for department in Department],
        verbose_name="Department")
    reporting_manager = models.CharField(max_length=36, null=True, verbose_name="Reporting Manager")
    joining_date = models.DateTimeField(verbose_name="Joining Date")


class IdProofs(models.Model):
    employee = models.CharField(max_length=36, verbose_name="Employee")
    pan_no = models.CharField(
        max_length=10, validators=[MinLengthValidator(10), validate_pan], verbose_name="PAN No")
    aadhar_no = models.CharField(
        max_length=14, validators=[MinLengthValidator(14), validate_aadhar], verbose_name="Aadhar No")
    pan_image = models.ImageField(upload_to=upload_pan_image_for_employee, max_length=500)
    aadhar_image = models.ImageField(upload_to=upload_aadhar_image_for_employee, max_length=500)


class SalaryAccount(models.Model):
    employee = models.CharField(max_length=36, unique=True, verbose_name="Employee")
    bank_name = models.CharField(max_length=60)
    account_no = models.CharField(max_length=18, validators=[MinLengthValidator(9), validate_bank_account_no])
    ifsc_code = models.CharField(max_length=11, validators=[MinLengthValidator(11), validate_ifsc_code])
    account_holder_name = models.CharField(max_length=60)


class Attendance(models.Model):
    employee = models.CharField(max_length=36, verbose_name='Employee')
    date = models.DateField()
    status = models.CharField(
        max_length=50, choices=[(attendance_status.value, attendance_status.value) for attendance_status in
                                AttendanceStatus], verbose_name="Status")

    class Meta:
        unique_together = ('employee', 'date')


class Leaves(models.Model):
    employee = models.CharField(max_length=36, verbose_name="Employee")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(choices=[(status.name, status.value) for status in LeaveStatus], max_length=36)
    approved_by = models.CharField(max_length=36, verbose_name="Approved By")
    leave_type = models.CharField(max_length=36, choices=[(type.name, type.value) for type in LeaveType], verbose_name='Leave type')

    class Meta:
        unique_together = ('employee', 'date', )

class Salary(models.Model):
    employee = models.CharField(max_length=36, unique=True, verbose_name="Employee ID")
    year_salary = models.IntegerField()
