from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import JobList, JobDetail, JobApplicationsList, JobApplicationsDetail, GetActiveApplicationsForJobDetail


urlpatterns = [
    # job applications for a job
    path('applications/active/<str:job_id>/', GetActiveApplicationsForJobDetail.as_view()),

    # urls for job application
    path('application/', JobApplicationsList.as_view()),
    path('application/<str:pk>/', JobApplicationsDetail.as_view()),

    # urls for job
    path('', JobList.as_view()),
    path('<str:pk>/', JobDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
