"""ChillBro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='ChillBro APIs')


urlpatterns = [
    path('api_documentation/', schema_view),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('coupons/', include('Coupons.urls')),
    path('issues/', include('Issues.urls')),
    path('address/', include('Address.urls')),
    path('bookings/', include('Bookings.urls')),
    path('review/', include('ReviewsRatings.urls')),
    path('payments/', include('Payments.urls')),
    path('user/', include('UserApp.urls')),
    path('entity/', include('Entity.urls')),
    path('refer/', include('Refer.urls')),
    path('cart/', include('Cart.urls')),
    path('wishlist/', include('WishList.urls')),
    path('wallet/', include('Wallet.urls')),
    path('notification/', include('Notifications.urls')),
    path('helpcenter/', include('HelpCenter.urls')),
    path('employee/', include('EmployeeManagement.urls')),
    path('jobs/', include('JobPortal.urls')),
    path('', include('Product.urls')),
]
