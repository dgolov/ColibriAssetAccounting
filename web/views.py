from django.views import View
from django.shortcuts import render
from web.models import Asset


class MainView(View):
    """ Представление главной страницы
    """
    def get(self, request, *args, **kwargs):
        context = {
            "title": "Main page",
            "assets": Asset.objects.filter(is_active=True)
        }
        return render(request, 'web/index.html', context)
