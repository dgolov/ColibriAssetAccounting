from django.urls import path
from django.views.decorators.cache import cache_page

import web.views as views


urlpatterns = [
    path('', cache_page(60)(views.MainView.as_view()), name='home'),
]