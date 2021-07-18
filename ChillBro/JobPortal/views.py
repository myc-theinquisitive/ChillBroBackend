from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from .models import Job, JobApplications
from .serializers import JobSerializer, JobApplicationsSerializer
from rest_framework.permissions import IsAuthenticated
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsGet, IsOwner
import json
from rest_framework.response import Response
from rest_framework import status
from .helpers import get_date_format


class JobList(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet,)

    def post(self, request, *args, **kwargs):
        basic_qualifications = request.data.pop("basic_qualifications", "[]")
        preferred_qualifications = request.data.pop("preferred_qualifications", "[]")
        request.data["basic_qualifications"] = json.dumps(basic_qualifications)
        request.data["preferred_qualifications"] = json.dumps(preferred_qualifications)
        return super().post(request, args, kwargs)


class JobDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet,)

    def put(self, request, *args, **kwargs):
        basic_qualifications = request.data.pop("basic_qualifications", "[]")
        preferred_qualifications = request.data.pop("preferred_qualifications", "[]")
        request.data["basic_qualifications"] = json.dumps(basic_qualifications)
        request.data["preferred_qualifications"] = json.dumps(preferred_qualifications)
        return super().put(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response({"message": "Job disabled successfully"}, status=status.HTTP_200_OK)


class JobApplicationsList(generics.ListCreateAPIView):
    queryset = JobApplications.objects.all()
    serializer_class = JobApplicationsSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsGet,)

    def post(self, request, *args, **kwargs):
        if "job" not in request.data:
            return Response({"message": "Cannot Apply for the job", "errors": "Job Id is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            job = Job.objects.get(id=request.data["job"])
        except ObjectDoesNotExist:
            return Response({"message": "Cannot Apply for the job", "errors": "Invalid Job Id"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not job.is_active:
            return Response({"message": "Cannot Apply for the job", "errors": "Job is not active"},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["created_by"] = request.user.id
        return super().post(request, args, kwargs)


class JobApplicationsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobApplications.objects.all()
    serializer_class = JobApplicationsSerializer
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee | IsOwner | IsGet,)

    def put(self, request, *args, **kwargs):
        if "job" not in request.data:
            return Response({"message": "Cannot update Job Application", "errors": "Job Id is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            job = Job.objects.get(id=request.data["job"])
        except ObjectDoesNotExist:
            return Response({"message": "Cannot update Job Application", "errors": "Invalid Job Id"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not job.is_active:
            return Response({"message": "Cannot update Job Application", "errors": "Job is not active"},
                            status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        self.check_object_permissions(request, instance)
        request.data["created_by"] = instance.created_by_id
        return super().put(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        instance.is_withdrawn = True
        instance.save()
        return Response({"message": "Job Application withdrawn successfully"}, status=status.HTTP_200_OK)


class GetActiveApplicationsForJobDetail(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsSuperAdminOrMYCEmployee,)
    queryset = JobApplications.objects.all()
    serializer_class = JobApplicationsSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = JobApplications.objects.active().filter(job_id=kwargs["job_id"])
        response = super().get(request, args, kwargs)

        job_application_ids = []
        for job_application in response.data["results"]:
            job_application_ids.append(job_application["id"])

        active_job_applications = JobApplications.objects.select_related('created_by')\
            .filter(id__in=job_application_ids)
        response_data = []
        for job_application in active_job_applications:
            job_application_data = {
                "applied_by": {
                    "name": job_application.created_by.first_name + " " + job_application.created_by.last_name,
                    "email": job_application.created_by.email
                },
                "application_status": job_application.application_status,
                "applied_on": job_application.applied_on.strftime(get_date_format())
            }
            response_data.append(job_application_data)

        response.data["results"] = response_data
        return response
