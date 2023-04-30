from django.views.generic import DetailView, ListView, CreateView
from django.shortcuts import render
from web.models import Asset


class MainView(ListView):
    """ Представление главной страницы
    """
    model = Asset
    template_name = 'web/index.html'
    context_object_name = 'assets'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data()
        context['title'] = 'Main page'
        return context

    def get_queryset(self):
        return Asset.objects.filter(is_active=True).order_by('name')
