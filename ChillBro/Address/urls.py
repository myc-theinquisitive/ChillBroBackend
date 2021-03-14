from django.urls import path
from .views import AddressList, AddressDetail, SpecificAddressList

urlpatterns = [
    path('', AddressList.as_view()),
    path('<int:pk>/', AddressDetail.as_view()),
    path('get_by_ids/', SpecificAddressList.as_view()),
]

