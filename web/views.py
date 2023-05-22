from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from web.models import Asset, AssetImage, Location, Order, History
from web import forms
from web.mixins import UserMixin


class Auth(View):
    def get(self, *args, **kwargs):
        auth_form = forms.AuthForm
        context = {
            'title': "Вход",
            'form': auth_form
        }
        return render(self.request, 'web/login.html', context)

    def post(self, request, *args, **kwargs):
        auth_form = forms.AuthForm(self.request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                pass
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(self.request, user)
                    return HttpResponseRedirect('/')
                else:
                    auth_form.add_error('__all__', 'Ошибка! Учетная запись пользователя не активна')
            else:
                auth_form.add_error('__all__', 'Ошибка! Проверьте правильность ввода данных')
        context = {
            'title': "Вход",
            'form': auth_form
        }
        return render(self.request, 'web/login.html', context)


class LogOut(View):
    def get(self, *args, **kwargs):
        auth_form = forms.AuthForm
        context = {
            'title': "Вход",
            'form': auth_form
        }
        logout(self.request)
        return render(self.request, 'web/login.html', context)


class AssetList(UserMixin, ListView):
    """ Представление главной страницы (список активов)
    """
    model = Asset
    template_name = 'web/index.html'
    context_object_name = 'assets'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetList, self).get_context_data()
        context['title'] = 'Активы'
        return context

    def get_queryset(self):
        return Asset.objects.filter(is_active=True).order_by('name')


class AssetDetail(UserMixin, DetailView):
    """ Детальное представление актива
    """
    model = Asset
    template_name = 'web/asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetDetail, self).get_context_data()
        context['title'] = f"Актив {self.get_object().name}"
        return context


class CreateAssert(UserMixin, CreateView):
    """ Создание нового актива
    """
    template_name = 'web/create_asset.html'
    form_class = forms.CreateAssetForm
    success_url = reverse_lazy('assets')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateAssert, self).get_context_data()
        context['title'] = 'Создание актива'
        context['form'] = forms.CreateAssetForm
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
        return HttpResponseRedirect('/')


class CreateAssertImage(UserMixin, CreateView):
    """ Загрузка изображения актива актива
    """
    # template_name = 'web/create_asset_image.html'
    # form_class = forms.CreateAssetForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateAssertImage, self).get_context_data()
        context['title'] = 'Добавление изображения к активу'
        return context

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect('/')

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
        return HttpResponseRedirect('/')


class DeleteAssertImage(UserMixin, DeleteView):
    model = AssetImage

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssertImage, self).get_context_data()
        context['title'] = 'Удаление изображения актива'
        return context

    def get_success_url(self):
        pass
        # self.request
        # return f'/assets/{self.get_object().pk}'


class UpdateAsset(UserMixin, UpdateView):
    """ Обновление актива
    """
    model = Asset
    template_name = 'web/update_asset.html'
    form_class = forms.UpdateAssetForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateAsset, self).get_context_data()
        try:
            asset = Asset.objects.get(pk=self.get_object().pk)
            context['asset'] = asset
        except Asset.DoesNotExist:
            return {}
        context['title'] = f'Обновление актива {asset.name}'
        context['form'] = forms.UpdateAssetForm(
            initial={
                'name': asset.name,
                'location': asset.location,
                'year_of_purchase': asset.year_of_purchase,
                'price': asset.price,
                'state': asset.state,
                'status': asset.status,
                'is_active': asset.is_active,
                'description': asset.description,
            }
        )
        return context

    def get_success_url(self):
        return f'/assets/{self.get_object().pk}'

    def put(self, *args, **kwargs):
        super(UpdateAsset, self).put(*args, **kwargs)


class DeleteAssert(UserMixin, DeleteView):
    """ Удаление актива
    """
    model = Asset
    # template_name = 'web/delete_asset.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssert, self).get_context_data()
        context['title'] = 'Удаление актива'
        return context


class LocationList(UserMixin, ListView):
    """ Список локаций
    """
    model = Location
    template_name = 'web/locations.html'
    context_object_name = 'locations'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationList, self).get_context_data()
        context['title'] = 'Склады'
        return context


class LocationDetail(UserMixin, DetailView):
    """ Детальное представление локаций
    """
    model = Location
    template_name = 'web/location_detail.html'
    context_object_name = 'location'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationDetail, self).get_context_data()
        context['title'] = f"Склад {self.get_object().name}"
        return context


class CreateLocation(UserMixin, CreateView):
    """ Создание местоположения
    """
    template_name = 'web/create_location.html'
    form_class = forms.LocationForm
    success_url = reverse_lazy('locations')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateLocation, self).get_context_data()
        context['title'] = 'Создание склада'
        context['form'] = forms.LocationForm
        return context


class UpdateLocation(UserMixin, UpdateView):
    """ Обновление местоположения
    """
    template_name = 'web/update_location.html'
    model = Location
    form_class = forms.LocationForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UpdateLocation, self).get_context_data()
        try:
            location = Location.objects.get(pk=self.get_object().pk)
            context['location'] = location
        except Location.DoesNotExist:
            return {}
        context['title'] = f'Обновление склада {location.name}'
        context['form'] = forms.LocationForm(
            initial={
                'name': location.name,
                'city': location.city,
                'address': location.address,
                'phone': location.phone,
                'description': location.description,
            }
        )
        return context

    def get_success_url(self):
        return f'/locations/{self.get_object().pk}'


class DeleteLocation(UserMixin, DeleteView):
    """ Удаление местоположения
    """
    model = Location
    # template_name = 'web/delete_location.html'
    success_url = reverse_lazy('locations')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteLocation, self).get_context_data()
        context['title'] = 'Удаление склада'
        return context


class OrderList(UserMixin, ListView):
    """ Список отчетов
    """
    model = Order
    template_name = 'web/orders.html'
    context_object_name = 'orders'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OrderList, self).get_context_data()
        context['title'] = 'Отчеты'
        return context


class CreateOrder(UserMixin, CreateView):
    """ Формировпние и загрузка отчета
    """
    # template_name = 'web/create_order.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateOrder, self).get_context_data()
        context['title'] = 'Создание отчета'
        return context

    def post(self, request, *args, **kwargs):
        super(CreateOrder, self).post(request, *args, **kwargs)
