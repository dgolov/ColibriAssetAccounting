from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.shortcuts import render
from web.models import Asset, AssetImage, Location, Order, History


class MainView(ListView):
    """ Представление главной страницы (список активов)
    """
    model = Asset
    template_name = 'web/index.html'
    context_object_name = 'assets'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MainView, self).get_context_data()
        context['title'] = 'Main page'
        return context

    def get_queryset(self):
        return Asset.objects.filter(is_active=True).order_by('name')


class AssetDetail(DetailView):
    """ Детальное представление актива
    """
    model = Asset
    context_object_name = 'assets'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetDetail, self).get_context_data()
        context['title'] = 'Asset'
        return context


class CreateAssert(CreateView):
    """ Создание нового актива
    """
    # template_name = 'crm/create_academic_performance.html'
    # form_class = forms.CreateAcademicPerformanceForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateAssert, self).get_context_data()
        context['title'] = 'Create asset'
        return context

    # def form_valid(self, form):
    #     form.save()
    #     return HttpResponseRedirect('/api/crm/academic-performance')
    #
    # def form_invalid(self, form):
    #     messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
    #     return HttpResponseRedirect('/api/crm/academic-performance')


class UpdateAsset(UpdateView):
    """ Обновление актива
    """
    model = Asset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateAsset, self).get_context_data()
        context['title'] = 'Update asset'
        return context


class DeleteAssert(DeleteView):
    """ Удаление актива
    """
    model = Asset
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssert, self).get_context_data()
        context['title'] = 'Delete asset'
        return context


class LocationList(ListView):
    """ Список локаций
    """
    model = Location
    context_object_name = 'locations'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationList, self).get_context_data()
        context['title'] = 'Locations'
        return context


class LocationDetail(DetailView):
    """ Детальное представление локаций
    """
    model = Location
    context_object_name = 'location'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationDetail, self).get_context_data()
        context['title'] = 'location Detail'
        return context


class CreateLocation(CreateView):
    """ Создание местоположения
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateLocation, self).get_context_data()
        context['title'] = 'Create location'
        return context


class UpdateLocation(UpdateView):
    """ Обновление местоположения
    """
    model = Location

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateLocation, self).get_context_data()
        context['title'] = 'Update location'
        return context


class DeleteLocation(DeleteView):
    """ Удаление местоположения
    """
    model = Location
    success_url = reverse_lazy('locations')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteLocation, self).get_context_data()
        context['title'] = 'Delete location'
        return context


class OrderList(ListView):
    """ Список отчетов
    """
    model = Order
    context_object_name = 'orders'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OrderList, self).get_context_data()
        context['title'] = 'Orders'
        return context


class CreateOrder(CreateView):
    """ Формировпние и загрузка отчета
    """

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateOrder, self).get_context_data()
        context['title'] = 'Create order'
        return context
