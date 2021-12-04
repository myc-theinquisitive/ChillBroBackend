from django.urls import path
from .views import AddressList, AddressDetail, SpecificAddressList, \
    UserSavedAddressView, UserSavedAddressDetailView, CitiesList

urlpatterns = [
    path('', AddressList.as_view()),
    path('get_by_ids/', SpecificAddressList.as_view()),
    path('user/save/', UserSavedAddressView.as_view()),
    path('user/save/<str:address_id>/', UserSavedAddressDetailView.as_view()),
    path('cities/', CitiesList.as_view()),
    path('<str:pk>/', AddressDetail.as_view()),
]

