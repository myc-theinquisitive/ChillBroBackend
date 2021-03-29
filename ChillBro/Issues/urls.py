from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *


urlpatterns = [
    path('new/',NewIssue.as_view(),name='new_issue'),
    path('<int:pk>/',SingleIssue.as_view(),name='single_issue'),
    path('close/',EditIssue.as_view(),{"status":3},name='edit_issue'),
    path('pick/', EditIssue.as_view(),{"status":2}, name='edit_issue'),
    path('close/user/', CloseIssueUser.as_view(), name='close_issue'),
    path('<int:current_department>/<int:status>/',DepartmentStatusIssues.as_view(),name='department_status_issues'),
    path('transfer/',TransferIssue.as_view(),name='transfer_issue'),
    path('transfer-history/',TransferHistory.as_view(),name='transfer_history')
    # path('transfer-close/', CloseTransfers.as_view(), name='transfer_issue'),
]


urlpatterns = format_suffix_patterns(urlpatterns)