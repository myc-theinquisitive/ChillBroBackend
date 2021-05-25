from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    path('business_client/', BusinessClientAdd.as_view(), name='new_business_client'),
    path('business_client_all/', BusinessClientAll.as_view(), name='all_business_client'),
    path('business_client/employees/', EntityBusinessClientEmployee.as_view()),
    path('business_client/<str:pk>/', BusinessClientDetail.as_view(), name='business_client_detail'),
    path('employee/', EmployeeAdd.as_view(), name='new_employee'),
    path('employee/image/', EmployeeImageCreate.as_view()),
    path('employee/image/<int:pk>/', EmployeeImageDelete.as_view()),
    path('employee/<str:pk>/', EmployeeDetail.as_view(), name='employee_detail'),
    path('<str:pk>/employee/active/', EmployeeActive.as_view(), name='employee_active'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
