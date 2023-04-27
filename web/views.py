from django.views import View
from django.shortcuts import render


class MainView(View):
    """ Представление главной страницы
    """
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'web/index.html', context)
