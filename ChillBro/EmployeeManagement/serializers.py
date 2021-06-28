from rest_framework import serializers
from .models import *


class MYCEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MYCEmployee
        fields = '__all__'


class IdProofsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdProofs
        fields = '__all__'


class SalaryAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryAccount
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def create(self, validated_data):
        return Attendance.objects.create(
            employee=validated_data["employee"],
            date=validated_data["date"],
            status=validated_data["status"]
        )

    def bulk_create(validated_data):
        attendances = []
        for attendance in validated_data:
            attendance_object = Attendance(
                employee=attendance["employee"],
                date=attendance["date"],
                status=attendance["status"]
            )
            attendances.append(attendance_object)
        Attendance.objects.bulk_create(attendances)


class LeavesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaves
        fields = "__all__"
