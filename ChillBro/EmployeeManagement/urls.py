from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [

    path('myc-employee/', MYCEmployeeList.as_view()),
    path('myc-employee/<str:employee>/', MYCEmployeeDetail.as_view()),
    path('id-proofs/', IdProofsList.as_view()),
    path('id-proofs/<str:employee>/', IdProofsDetail.as_view()),
    path('salary-account/', SalaryAccountList.as_view()),
    path('salary-account/<str:employee>/', SalaryAccountDetail.as_view()),
    path('department/<str:department>/', DepartmentWiseEmployee.as_view()),
    path('manager/<str:manager>/', ManagerWiseEmployee.as_view()),
    path('manager/all-levels/<str:manager>/', ManagerWiseAllLevelEmployee.as_view()),
    path('attendance/', AttendanceList.as_view()),
    path('attendance/department/', AttendanceList.as_view()),
    path('attendance/manager/', AttendanceList.as_view()),
    path('leaves/',LeavesList.as_view()),
    path('leaves/<str:pk>/',LeavesDetail.as_view()),
    path('pending-leaves/', PendingLeavesList.as_view()),

    # employee full details
    path('<str:employee_id>/', EmployeeFullDetails.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
