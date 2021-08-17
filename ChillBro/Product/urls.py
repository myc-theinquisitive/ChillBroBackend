from django.urls import path
from .views import ProductList, ProductDetail, GetProductsByCategory, SearchProducts, GetSellerProductList, \
    ProductNetPrice, BusinessClientProductsByVerificationStatus, BusinessClientProductDetails, \
    ProductVerificationDetail, ProductListBasedOnVerificationStatus, RentalProductsTypes, RentalHomePageCategories, \
    HotelProductsTypes, HotelEntityProducts
from .BaseProduct.views import ProductQuantity, BaseProductImageDelete, BaseProductImageCreate
from .Category.views import CategoryList, CategoryImageCreate, CategoryImageDelete, GetCategoriesLevelWise, \
    GetSpecificCategoriesLevelWise, CategoryTopLevelList, CategoryProductPricesList, \
    CategoryProductPricesDetail, CategoryDetail, CategoryProductList, CategoryProductDetail
from .Hotel.views import AmenitiesList, FindDistance, FindDistanceByAddress, FindDistanceForMultipleAddress
from .VehicleTypes.views import VehicleTypeList, VehicleTypeDetail, VehicleCharacteristicsList, \
    VehicleCharacteristicsDetail
from .Places.views import PlaceList, PlaceDetail, PlaceImageCreate, PlaceImageDelete, GetPlacesByCategory
from .TravelPackages.views import TravelPackageList, TravelPackageDetail, TravelPackageImageCreate, \
    TravelPackageImageDelete
from .TravelPackageVehicle.views import TravelPackageVehiclesList
from  .TravelAgency.views import TravelCharacteristicsList,TravelCharacteristicsDetail

urlpatterns = [

    # urls for category
    path('category/', CategoryList.as_view()),
    path('category/image/', CategoryImageCreate.as_view()),
    path('category/image/<str:pk>/', CategoryImageDelete.as_view()),
    path('category/level_wise/', GetCategoriesLevelWise.as_view()),
    path('category/level_wise/<str:slug>/', GetSpecificCategoriesLevelWise.as_view()),
    path('category/top_level/', CategoryTopLevelList.as_view()),

    path('category/product/', CategoryProductList.as_view()),
    path('category/product/<str:pk>/', CategoryProductDetail.as_view()),
    path('category/product/prices/', CategoryProductPricesList.as_view()),
    path('category/product/prices/<str:category_product>/', CategoryProductPricesDetail.as_view()),
    path('category/<str:pk>/', CategoryDetail.as_view()),

    # urls for vehicle
    path('vehicle/type/', VehicleTypeList.as_view()),
    path('vehicle/type/<str:pk>/', VehicleTypeDetail.as_view()),

    path('vehicle/characteristics/', VehicleCharacteristicsList.as_view()),
    path('vehicle/characteristics/<int:pk>/', VehicleCharacteristicsDetail.as_view()),

    # urls for place
    path('place/', PlaceList.as_view()),
    path('place/category/<str:slug>/', GetPlacesByCategory.as_view()),

    path('place/image/', PlaceImageCreate.as_view()),
    path('place/image/<int:pk>/', PlaceImageDelete.as_view()),
    path('place/<str:pk>/', PlaceDetail.as_view()),

    # urls for travel packages
    path('travel_package/', TravelPackageList.as_view()),
    path('travel_package/<str:travel_package_id>/vehicles/', TravelPackageVehiclesList.as_view()),
    path('travel_package/image/', TravelPackageImageCreate.as_view()),
    path('travel_package/image/<int:pk>/', TravelPackageImageDelete.as_view()),
    path('travel_package/<str:pk>/', TravelPackageDetail.as_view()),

    # urls for travel agency characteristics
    path('travel_agency/characteristics/',TravelCharacteristicsList.as_view()),
    path('travel_agency/characteristics/<str:id>/', TravelCharacteristicsDetail.as_view()),

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
    path('product/distance/', FindDistance.as_view()),
    path('product/distance/address/', FindDistanceByAddress.as_view()),
    path('product/distance/multiple-address/', FindDistanceForMultipleAddress.as_view()),

    # urls of update product
    path('product/quantity/<str:product_id>/', ProductQuantity.as_view()),

    path('product/rental_home_page_categories/', RentalHomePageCategories.as_view()),
    path('product/rental_products_types/', RentalProductsTypes.as_view()),
    path('product/hotel_products_types/', HotelProductsTypes.as_view()),
    path('product/entity/<str:seller_id>/',HotelEntityProducts.as_view()),

    path('product/category/<str:slug>/', GetProductsByCategory.as_view()),
    path('product/<str:id>/', ProductDetail.as_view()),

]
