# Create your views here.
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .helpers import MultipleFieldLookupMixin
from .constants import Status, default_final_resolution


class IssueList(APIView):
    serializer_class = IssueSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.data['user_id']=request.user.id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Issued inserted successfully", "issue id": serializer.data['id']},
                            status=status.HTTP_200_OK)
        else:
            return Response({"message": "Issue not inserted", "error": serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        issues = Issue.objects.all()
        serializer = self.serializer_class(issues, many=True)
        return Response(serializer.data)


class IssueDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


class EditIssue(APIView):
    serializer_class = EditIssueSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request, status_flag):
        try:
            issue = Issue.objects.get(pk=request.data['issue_id'])
        except:
            return Response({"error": "Issue doesn't exist"})
        request.data['status'] = status_flag
        if status_flag == Status.IN_PROGRESS.value:  # for issue to pick, final resolution need not be provided.
            request.data['final_resolution'] = default_final_resolution
        serializer = self.serializer_class(issue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CloseIssueUser(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CloseUserIssueSerializer

    def put(self, request):
        try:
            issue = Issue.objects.get(pk=request.data['issue_id'])
        except:
            return Response({"error": "Issue doesn't exist"})
        request.data['user_id'] = request.user.id
        request.data['status'] = Status.DONE.value
        request.data['final_resolution'] = "Issue closed by user"
        request.data['current_employeeId'] = None
        serializer = self.serializer_class(issue, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepartmentStatusIssues(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    lookup_fields = ['current_department', 'status']


class TransferIssue(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def post(self, request):
        request.data['updated_at'] = timezone.now()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            issue_id = request.data['issue_id']
            issue = Issue.objects.get(id=issue_id)
            issue.status = Status.TODO.value
            issue.current_department = request.data['transferred_to']
            issue.current_employeeId = None
            issue.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class TransferHistory(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def get_queryset(self):
        queryset = Transfer.objects.filter(issue_id=self.kwargs['issue_id']).order_by('created_at')
        return queryset
