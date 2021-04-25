from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *
from .constants import Status

urlpatterns = [
    path('', IssueList.as_view(), name='new_issue'),
    path('transfer/', TransferIssue.as_view(), name='transfer_issue'),
    path('close/<str:issue_id>/', PickCloseIssue.as_view(), {"status_flag": Status.DONE.value}, name='edit_issue'),
    path('pick/<str:issue_id>/', PickCloseIssue.as_view(), {"status_flag": Status.IN_PROGRESS.value}, name='edit_issue'),
    path('close/user/<str:issue_id>/', CloseIssueUser.as_view(), name='close_issue'),
    path('transfer_history/<str:issue_id>/', TransferHistory.as_view(), name='transfer_history'),
    path('<str:pk>/', IssueDetail.as_view(), name='issue_detail'),
    path('<str:current_department>/<str:status>/', DepartmentStatusIssues.as_view(), name='department_status_issues'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
