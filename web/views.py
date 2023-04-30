from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from web.models import Asset, AssetImage, Location, Order, History
from web import forms


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
    # template_name = 'crm/asset_detail.html'
    context_object_name = 'assets'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetDetail, self).get_context_data()
        context['title'] = 'Asset'
        return context


class CreateAssert(CreateView):
    """ Создание нового актива
    """
    # template_name = 'crm/create_asset.html'
    form_class = forms.CreateAssetForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateAssert, self).get_context_data()
        context['title'] = 'Create asset'
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
        return HttpResponseRedirect('/')


class UpdateAsset(UpdateView):
    """ Обновление актива
    """
    model = Asset
    # template_name = 'crm/update_asset.html'
    form_class = forms.UpdateAssetForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateAsset, self).get_context_data()
        context['title'] = 'Update asset'
        return context

    def get_success_url(self):
        return f'/assets/{self.get_object().pk}'


class DeleteAssert(DeleteView):
    """ Удаление актива
    """
    model = Asset
    # template_name = 'crm/delete_asset.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssert, self).get_context_data()
        context['title'] = 'Delete asset'
        return context


class LocationList(ListView):
    """ Список локаций
    """
    model = Location
    # template_name = 'crm/locations.html'
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
    # template_name = 'crm/location_detail.html'
    context_object_name = 'location'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationDetail, self).get_context_data()
        context['title'] = 'location Detail'
        return context


class CreateLocation(CreateView):
    """ Создание местоположения
    """
    # template_name = 'crm/create_location.html'
    form_class = forms.LocationForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateLocation, self).get_context_data()
        context['title'] = 'Create location'
        return context


class UpdateLocation(UpdateView):
    """ Обновление местоположения
    """
    # template_name = 'crm/update_location.html'
    model = Location
    form_class = forms.LocationForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateLocation, self).get_context_data()
        context['title'] = 'Update location'
        return context

    def get_success_url(self):
        return f'/locations/{self.get_object().pk}'


class DeleteLocation(DeleteView):
    """ Удаление местоположения
    """
    model = Location
    # template_name = 'crm/delete_location.html'
    success_url = reverse_lazy('locations')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteLocation, self).get_context_data()
        context['title'] = 'Delete location'
        return context


class OrderList(ListView):
    """ Список отчетов
    """
    model = Order
    # template_name = 'crm/orders.html'
    context_object_name = 'orders'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OrderList, self).get_context_data()
        context['title'] = 'Orders'
        return context


class CreateOrder(CreateView):
    """ Формировпние и загрузка отчета
    """
    # template_name = 'crm/create_order.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateOrder, self).get_context_data()
        context['title'] = 'Create order'
        return context

    def post(self, request, *args, **kwargs):
        super(CreateOrder, self).post(request, *args, **kwargs)
