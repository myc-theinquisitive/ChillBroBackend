import django
from django.http import HttpResponse, JsonResponse

# Create your views here.
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,mixins,generics
from rest_framework.permissions import IsAuthenticated
from .helpers import MultipleFieldLookupMixin


class NewIssue(APIView):
    serializer_class=IssueSerializer
    # permission_classes = (IsAuthenticated,)
    def post(self,request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Issued inserted successfully","issue id":serializer.id},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Issue not inserted","error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

class SingleIssue(generics.RetrieveUpdateDestroyAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    lookup_field = 'pk'

class EditIssue(APIView):
    serializer_class=EditIssueSerializer
    # permission_classes = (IsAuthenticated,)
    def put(self,request,status):
        try:
            issue = Issue.objects.get(pk=request.data['issue_id'])
        except:
            return Response({"error":"Issue does'nt exist"})
        request.data['status']=status
        request.data['updated_at']=timezone.now()
        if status==2:  # for issue to pick, final resolution need not be provided.
            request.data['final_resolution']="Issue is not yet resolved"
        serializer = self.serializer_class(issue,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CloseIssueUser(APIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class=EditIssueSerializer
    def put(self,request):
        try:
            issue = Issue.objects.get(pk=request.data['issue_id'])
        except:
            return Response({"error":"Issue does'nt exist"})
        if 'user_id' not in request.data:
            return Response({"error":"User Id is required"})
        request.data['status']=3
        request.data['updated_at']=timezone.now()
        request.data['final_resolution']="Issue closed by user"
        request.data['current_emplooyeId']=" "
        serializer = self.serializer_class(issue,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class DepartmentStatusIssues(MultipleFieldLookupMixin, generics.RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    lookup_fields = ['current_department','status']


class TransferIssue(APIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = TransferSerializer

    def put(self,request):
        request.data['updated_at'] = timezone.now()
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            issue_id = request.data['issue_id']
            issue = Issue.objects.get(id=issue_id)
            issue.status = 1
            issue.current_department=request.data['department']
            issue.save()
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)

class TransferHistory(APIView):
    serializer_class = TransferHistorySerializer
    def get(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            issues=Transfer.objects.filter(issue_id=request.data['issue_id']).order_by('created_at')
            response = django.core.serializers.serialize("json", issues)
            return Response(response, content_type='application/json',status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)