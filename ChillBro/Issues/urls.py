from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *
from .constants import Status

urlpatterns = [
    path('', IssueList.as_view(), name='new_issue'),
    path('<str:pk>/', IssueDetail.as_view(), name='issue_detail'),
    path('close/', EditIssue.as_view(), {"status_flag": Status.DONE.value}, name='edit_issue'),
    path('pick/', EditIssue.as_view(), {"status_flag": Status.IN_PROGRESS.value}, name='edit_issue'),
    path('close/user/', CloseIssueUser.as_view(), name='close_issue'),
    path('<str:current_department>/<str:status>/', DepartmentStatusIssues.as_view(), name='department_status_issues'),
    path('transfer/', TransferIssue.as_view(), name='transfer_issue'),
    path('transfer-history/<int:issue_id>', TransferHistory.as_view(), name='transfer_history')
]

urlpatterns = format_suffix_patterns(urlpatterns)
