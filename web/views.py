from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.shortcuts import render
from web.models import Asset, AssetImage, Location, Order, History


class MainView(ListView):
    """ Представление главной страницы (список активов)
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


class AssetDetail(DetailView):
    """ Детальное представление актива
    """
    pass


class CreateAssert(CreateView):
    """ Создание нового актива
    """
    pass


class UpdateAsset(UpdateView):
    """ Обновление актива
    """
    pass


class DeleteAssert(DeleteView):
    """ Удаление актива
    """
    pass


class CreateLocation(CreateView):
    """ Создание местоположения
    """
    pass


class UpdateLocation(UpdateView):
    """ Обновление местоположения
    """
    pass


class DeleteLocation(DeleteView):
    """ Удаление местоположения
    """
    pass


class CreateOrder(CreateView):
    """ Формировпние и загрузка отчета
    """
    pass
