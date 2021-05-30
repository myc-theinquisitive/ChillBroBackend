from django.urls import path
from .views import ProductList, ProductDetail, GetProductsByCategory, SearchProducts, GetSellerProductList, \
    ProductNetPrice, BusinessClientProductsByVerificationStatus, BusinessClientProductDetails, \
    ProductVerificationDetail, ProductListBasedOnVerificationStatus
from .BaseProduct.views import ProductQuantity, BaseProductImageDelete, BaseProductImageCreate
from .Category.views import CategoryList, CategoryImageCreate, CategoryImageDelete, GetCategoriesLevelWise, \
    GetSpecificCategoriesLevelWise, CategoryTopLevelList, CreateCategoryPrices, GetCategoryPrices, CategoryDetail
from .Hotel.views import AmenitiesList


urlpatterns = [

    # urls for category
    path('category/', CategoryList.as_view()),
    path('category/image/', CategoryImageCreate.as_view()),
    path('category/image/<str:pk>/', CategoryImageDelete.as_view()),
    path('category/level_wise/', GetCategoriesLevelWise.as_view()),
    path('category/level_wise/<str:slug>/', GetSpecificCategoriesLevelWise.as_view()),
    path('category/top_level/', CategoryTopLevelList.as_view()),
    path('category/prices/', CreateCategoryPrices.as_view()),
    path('category/get_prices/<int:category>/', GetCategoryPrices.as_view()),
    path('category/<str:pk>/', CategoryDetail.as_view()),

    # urls for all products
    path('product/', ProductList.as_view()),

    # urls for verification
    path('product/verification/<str:product_id>/', ProductVerificationDetail.as_view()),
    path('product/verification_status/<str:status>/', ProductListBasedOnVerificationStatus.as_view()),

    # url of net prices
    path('product/net_price/', ProductNetPrice.as_view()),

    path('product/business_client/verification_status/', BusinessClientProductsByVerificationStatus.as_view()),
    path('product/seller/<str:seller_id>/', GetSellerProductList.as_view()),

    path('product/image/', BaseProductImageCreate.as_view()),
    path('product/image/<int:pk>/', BaseProductImageDelete.as_view()),
    path('product/search/<str:query>/', SearchProducts.as_view()),
    path('product/business_client/<str:product_id>/', BusinessClientProductDetails.as_view()),

    # urls specific to hotels
    path('product/amenities/', AmenitiesList.as_view()),

    #url of update product
    path('product/quantity/<str:product_id>/', ProductQuantity.as_view()),

    path('product/category/<str:slug>/', GetProductsByCategory.as_view()),
    path('product/<str:id>/', ProductDetail.as_view()),
]
