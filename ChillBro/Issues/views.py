from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.generics import ListCreateAPIView
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .constants import Status, DEFAULT_FINAL_RESOLUTION, USER_CLOSED_RESOLUTION
from .wrappers import is_order_id_valid, is_product_id_valid
from ChillBro.permissions import IsSuperAdminOrMYCEmployee, IsOwner


class IssueList(ListCreateAPIView):
    serializer_class = IssueSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data['created_by'] = request.user.id
        serializer = self.serializer_class(data=request.data)

        if not is_product_id_valid(request.data['product_id']):
            return Response({"message": "Issue not inserted", "error": "Invalid Product Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not is_order_id_valid(request.data['order_id']):
            return Response({"message": "Issue not inserted", "error": "Invalid Order Id"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not serializer.is_valid():
            return Response({"message": "Issue not inserted", "error": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

        images = request.data.pop("images", [])
        issue = serializer.create(request.data.dict())

        issue_image_dicts = []
        for image in images:
            issue_image_dict = {
                "issue": issue,
                "image": image
            }
            issue_image_dicts.append(issue_image_dict)
        IssueImageSerializer.bulk_create(issue_image_dicts)

        return Response({"message": "Issued inserted successfully", "issue_id": issue.id},
                        status=status.HTTP_200_OK)


class IssueDetail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        issue = self.get_object()
        images = IssueImage.objects.filter(issue=issue).values_list("image", flat=True)
        response.data["images"] = images
        return response


class PickCloseIssue(APIView):
    serializer_class = PickCloseIssueSerializer
    permission_classes = (IsAuthenticated & IsSuperAdminOrMYCEmployee,)

    def put(self, request, issue_id, status_flag):
        with transaction.atomic():
            try:
                issue = Issue.objects.select_for_update().get(pk=issue_id)
            except ObjectDoesNotExist:
                return Response({"message": "Issue can't be picked/closed", "error": "Invalid Issue"},
                                status=status.HTTP_400_BAD_REQUEST)

            if issue.status == Status.DONE.value:
                return Response({"message": "Issue can't be picked/closed", "error": "Issue already closed"},
                                status=status.HTTP_400_BAD_REQUEST)

            request.data['status'] = status_flag
            request.data['current_employee_id'] = request.user.id
            if status_flag == Status.IN_PROGRESS.value:  # for issue to pick, final resolution need not be provided.
                if issue.current_employee_id is not None:
                    return Response({"message": "Issue can't be picked", "error": "Issue already picked"},
                                    status=status.HTTP_400_BAD_REQUEST)
                request.data['final_resolution'] = DEFAULT_FINAL_RESOLUTION
            else:
                # for closing an issue
                if issue.current_employee_id != str(request.user.id):
                    return Response({"message": "Issue can't be closed", "error": "You can't close this Issue"},
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(issue, data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CloseIssueUser(APIView):
    permission_classes = (IsAuthenticated & IsOwner,)
    serializer_class = CloseUserIssueSerializer

    def put(self, request, issue_id):
        with transaction.atomic():
            try:
                issue = Issue.objects.select_for_update().get(pk=issue_id)
            except ObjectDoesNotExist:
                return Response({"message": "Issue can't be closed", "error": "Invalid Issue"},
                                status=status.HTTP_400_BAD_REQUEST)

            self.check_object_permissions(request, issue)

            if issue.status == Status.DONE.value:
                return Response({"message": "Issue can't be closed", "error": "Issue already closed"},
                                status=status.HTTP_400_BAD_REQUEST)

            request.data['status'] = Status.DONE.value
            request.data['final_resolution'] = USER_CLOSED_RESOLUTION
            request.data['current_employee_id'] = None
            serializer = self.serializer_class(issue, data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class DepartmentStatusIssues(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = IssueSerializer

    def get_queryset(self):
        queryset = Issue.objects.filter(
            current_department=self.kwargs['current_department'], status=self.kwargs['status']).order_by('created_at')
        return queryset


class TransferIssue(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            issue = Issue.objects.get(pk=request.data['issue_id'])
        except ObjectDoesNotExist:
            return Response({"message": "Issue can't be transferred", "error": "Invalid Issue"},
                            status=status.HTTP_400_BAD_REQUEST)

        if issue.status == Status.DONE.value:
            return Response({"message": "Issue can't be transferred", "error": "Issue already closed"},
                            status=status.HTTP_400_BAD_REQUEST)

        if issue.current_employee_id != str(request.user.id):
            return Response({"message": "Issue can't be transferred", "error": "You can't transfer this Issue"},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data["transferred_by"] = request.user.id
        request.data["issue"] = issue.id

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        issue.status = Status.TODO.value
        issue.current_department = request.data['transferred_to']
        issue.current_employee_id = None
        issue.save()

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransferHistory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def get_queryset(self):
        queryset = Transfer.objects.filter(issue_id=self.kwargs['issue_id']).order_by('created_at')
        return queryset
