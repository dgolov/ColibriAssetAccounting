from django.urls import path
from django.views.decorators.cache import cache_page

import web.views as views


urlpatterns = [
    path('', cache_page(60)(views.AssetList.as_view()), name='assets'),
    path('/<int:pk>', cache_page(60)(views.AssetDetail.as_view()), name='assets_detail'),
    path('locations', cache_page(60)(views.LocationList.as_view()), name='locations'),
    path('locations/<int:pk>', cache_page(60)(views.LocationDetail.as_view()), name='locations_detail'),
    path('orders', cache_page(60)(views.OrderList.as_view()), name='orders'),
]
