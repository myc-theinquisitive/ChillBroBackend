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

class CloseUserIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['final_resolution', 'status','user_id','current_employeeId']


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'
