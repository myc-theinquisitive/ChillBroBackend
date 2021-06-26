import json
from rest_framework import serializers
from .models import Job, JobApplications


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('created_at', )

    def to_representation(self, instance):
        data = super(JobSerializer, self).to_representation(instance)
        data["basic_qualifications"] = json.loads(data["basic_qualifications"])
        data["preferred_qualifications"] = json.loads(data["preferred_qualifications"])
        return data


class JobApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplications
        fields = '__all__'
        read_only_fields = ('applied_on', )
