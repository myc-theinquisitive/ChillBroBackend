from rest_framework import serializers
from .models import *


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"

class EditIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['issue_id', 'final_resolution', 'status', 'current_employeeId']

    issue_id = serializers.CharField(required=True)
    final_resolution = serializers.CharField(max_length=200, required=True)
    status = serializers.CharField(max_length=200, required=True)
    current_employeeId = serializers.CharField(max_length=30, allow_blank=True)

class CloseUserIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['final_resolution', 'status','user_id','current_employeeId']


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class TransferHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = ['issue_id']
