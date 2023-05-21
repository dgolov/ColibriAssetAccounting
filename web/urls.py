from django.urls import path

import web.views as views


urlpatterns = [
    path('', views.AssetList.as_view(), name='assets'),
    path('auth', views.Auth.as_view(), name='auth'),
    path('logout', views.LogOut.as_view(), name='logout'),
    path('assets/<int:pk>', views.AssetDetail.as_view(), name='assets_detail'),
    path('locations', views.LocationList.as_view(), name='locations'),
    path('locations/<int:pk>', views.LocationDetail.as_view(), name='locations_detail'),
    path('orders', views.OrderList.as_view(), name='orders'),
]
