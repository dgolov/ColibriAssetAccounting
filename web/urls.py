from django.urls import path

import web.views as views


urlpatterns = [
    path('', views.AssetList.as_view(), name='assets'),
    path('auth', views.Auth.as_view(), name='auth'),
    path('logout', views.LogOut.as_view(), name='logout'),
    path('assets/<int:pk>', views.AssetDetail.as_view(), name='assets_detail'),
    path('assets/<int:pk>/add-image', views.CreateAssertImage.as_view(), name='create_asset_image'),
    path('assets/<int:asset-pk>/remove-image/<int:pk>', views.DeleteAssertImage.as_view(), name='delete_asset_image'),
    path('assets/create', views.CreateAssert.as_view(), name='create_asset'),
    path('assets/update/<int:pk>', views.UpdateAsset.as_view(), name='update_asset'),
    path('assets/delete/<int:pk>', views.DeleteAssert.as_view(), name='delete_asset'),
    path('locations', views.LocationList.as_view(), name='locations'),
    path('locations/<int:pk>', views.LocationDetail.as_view(), name='locations_detail'),
    path('locations/create', views.CreateLocation.as_view(), name='create_location'),
    path('locations/update/<int:pk>', views.UpdateLocation.as_view(), name='update_location'),
    path('locations/delete/<int:pk>', views.DeleteLocation.as_view(), name='delete_location'),
    path('orders', views.OrderList.as_view(), name='orders'),
    path('orders/create', views.CreateOrder.as_view(), name='create_order'),
]
