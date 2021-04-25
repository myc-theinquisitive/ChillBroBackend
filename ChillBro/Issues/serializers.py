from rest_framework import serializers
from .models import *


class IssueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueImage
        fields = '__all__'

    @staticmethod
    def bulk_create(issue_images):
        all_images = []
        for image in issue_images:
            each_image = IssueImage(
                issue=image['issue'],
                image=image['image']
            )
            all_images.append(each_image)
        return IssueImage.objects.bulk_create(all_images)


class IssueSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.FileField(), write_only=True
    )

    class Meta:
        model = Issue
        fields = "__all__"

    def create(self, validated_data):
        return Issue.objects.create(
            created_by_id=validated_data["created_by"], title=validated_data["title"],
            description=validated_data["description"], entity_id=validated_data["entity_id"],
            order_id=validated_data["order_id"], product_id=validated_data["product_id"]
        )


class PickCloseIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['final_resolution', 'status', 'current_employee_id']

    final_resolution = serializers.CharField(required=True)
    current_employee_id = serializers.CharField(max_length=36, required=True)


class CloseUserIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['final_resolution', 'status', 'current_employee_id']


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'
