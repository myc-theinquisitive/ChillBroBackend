from django.urls import path, re_path
from .views import CategoryList, CategoryDetail, CategoryImageCreate, GetCategoriesLevelWise, \
    BaseProductImageCreate, AmenitiesList, ProductList, ProductDetail, \
    GetProductsByCategory, GetSpecificCategoriesLevelWise, CategoryImageDelete, BaseProductImageDelete, \
    SearchProducts, GetSellerProductList, CategoryTopLevelList, \
    ProductNetPrice, ProductSellerStatus, ProductQuantity, BusinessClientProductDetails


urlpatterns = [

    # urls for category
    path('category/', CategoryList.as_view()),
    path('category/<int:pk>/', CategoryDetail.as_view()),
    path('category/image/', CategoryImageCreate.as_view()),
    path('category/image/<int:pk>/', CategoryImageDelete.as_view()),
    path('category/level_wise/', GetCategoriesLevelWise.as_view()),
    re_path('^category/level_wise/(?P<slug>[-\w]+)/$', GetSpecificCategoriesLevelWise.as_view()),
    path('category/top_level/', CategoryTopLevelList.as_view()),

    # urls for all products
    path('product/', ProductList.as_view()),

    # url of net prices
    path('product/net_price/', ProductNetPrice.as_view()),


    path('product/image/', BaseProductImageCreate.as_view()),
    path('product/image/<int:pk>/', BaseProductImageDelete.as_view()),
    path('product/search/<str:query>/', SearchProducts.as_view()),
    path('product/business_client/<str:product_id>/', BusinessClientProductDetails.as_view()),

    # urls specific to hotels
    path('product/amenities/', AmenitiesList.as_view()),

    path('product/seller/<str:seller_id>/', GetSellerProductList.as_view()),
    path('product/seller/<str:seller_id>/<str:status>/', ProductSellerStatus.as_view()),

    #url of update product
    path('product/quantity/<str:product_id>/', ProductQuantity.as_view()),

    path('product/<str:id>/', ProductDetail.as_view()),
    re_path('^product/category/(?P<slug>[-\w]+)/$', GetProductsByCategory.as_view()),
]
