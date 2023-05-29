from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from redis.exceptions import ConnectionError
from web.models import Asset, AssetImage, Location, Order, History
from web import forms
from web.mixins import UserMixin, AssetMixin


import logging


logger = logging.getLogger('main')


class Auth(View):
    """ Вход в систему
    """
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
            except User.DoesNotExist as e:
                logger.error(f"[Auth POST] Get user {username} error - {e}")
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    logger.debug(f'User login {username} success')
                    login(self.request, user)
                    return HttpResponseRedirect('/')
                else:
                    logger.debug(f'User login {username} is not active')
                    auth_form.add_error('__all__', 'Ошибка! Учетная запись пользователя не активна')
            else:
                logger.debug(f'User login {username} failed')
                auth_form.add_error('__all__', 'Ошибка! Проверьте правильность ввода данных')
        context = {
            'title': "Вход",
            'form': auth_form
        }
        return render(self.request, 'web/login.html', context)


class LogOut(View):
    """ Выход из системы
    """
    def get(self, *args, **kwargs):
        auth_form = forms.AuthForm
        context = {
            'title': "Вход",
            'form': auth_form
        }
        logger.debug(f'User logout {self.request.user.username} success')
        logout(self.request)
        return render(self.request, 'web/login.html', context)


class Profile(View):
    """ Личный кабинет пользователя
    """
    def get(self, *args, **kwargs):
        context = {
            'title': f'Личный кабинет',
            'form': forms.ProfileForm(
                initial={
                    'first_name': self.request.user.first_name,
                    'last_name': self.request.user.last_name,
                    'email': self.request.user.email,
                }
            )
        }
        return render(self.request, 'web/profile.html', context)

    def post(self, *args, **kwargs):
        form = forms.ProfileForm(self.request.POST)
        if form.is_valid():
            if form.data.get('first_name'):
                logger.debug(f'[Profile] Updated first_name for user: {self.request.user.username}')
                self.request.user.first_name = form.data.get('first_name')
            if form.data.get('last_name'):
                logger.debug(f'[Profile] Updated last_name for user: {self.request.user.username}')
                self.request.user.last_name = form.data.get('last_name')
            if form.data.get('email'):
                logger.debug(f'[Profile] Updated email for user: {self.request.user.username}')
                self.request.user.email = form.data.get('email')
            if form.data.get('password'):
                logger.debug(f'[Profile] Updated password for user: {self.request.user.username}')
                self.request.user.set_password(form.data.get('password'))
            self.request.user.save()
        return HttpResponseRedirect('/')


class AssetList(UserMixin, ListView):
    """ Представление главной страницы (список активов)
    """
    model = Asset
    template_name = 'web/index.html'
    context_object_name = 'assets'
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetList, self).get_context_data()

        search = self.request.GET.get('search')
        location_pk = self.request.GET.get('location')

        if location_pk:
            context['assets'] = Asset.objects.filter(location_id=location_pk)
        elif search:
            context['assets'] = Asset.objects.filter(name__iregex=search)

        context['title'] = 'Активы'
        context['locations'] = Location.objects.all()
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
        asset = form.save()
        logger.warning(f"[CreateAssert] Create asset successfully: {form.data}")
        History.objects.create(asset=asset, event_name="Создание актива")
        return HttpResponseRedirect('/')

    def form_invalid(self, form):
        logger.warning(f"[CreateAssert] Invalid form data: {form.data}")
        messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
        return HttpResponseRedirect('/')


class CreateAssertImage(UserMixin, CreateView):
    """ Загрузка изображения актива актива
    """
    template_name = 'web/create_asset_image.html'
    form_class = forms.CreateAssetImageForm
    _object_pk = None
    
    def get(self, request, *args, **kwargs):
        self._object_pk = kwargs.get('pk')
        return super(CreateAssertImage, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._object_pk = kwargs.get('pk')
        return super(CreateAssertImage, self).post(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreateAssertImage, self).get_context_data()
        try:
            asset = Asset.objects.get(pk=self._object_pk)
        except Asset.DoesNotExist as e:
            logger.error(f"Create asset error - {e}")
            return {}
        context['title'] = f'Добавление изображения к активу {asset.name}'
        context['asset'] = asset
        context['form'] = forms.CreateAssetImageForm(
            initial={
                'asset': asset.pk
            }
        )
        return context

    def form_valid(self, form):
        form.save()
        logger.debug(f"Upload asset image for asset id {self._object_pk} successfully")
        return HttpResponseRedirect(f'/assets/{self._object_pk}')

    def form_invalid(self, form):
        logger.warning(f"Upload asset image for asset id {self._object_pk} error")
        messages.add_message(self.request, messages.ERROR, 'Ошибка создания записи. Введены некорректные данные.')
        return HttpResponseRedirect(f'/assets/{self._object_pk}')


class DeleteAssertImage(UserMixin, DeleteView):
    """ Удаление изображения актива
    """
    model = AssetImage

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssertImage, self).get_context_data()
        context['title'] = 'Удаление изображения актива'
        return context

    def get_success_url(self):
        pass
        # self.request
        # return f'/assets/{self.get_object().pk}'


class UpdateAsset(UserMixin, AssetMixin, UpdateView):
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
        except Asset.DoesNotExist as e:
            logger.error(f"[UpdateAsset GET] Update asset error - {e}")
            return {}
        context['title'] = f'Обновление актива {asset.name}'
        context['form'] = forms.UpdateAssetForm(
            initial={
                'name': asset.name,
                'location': asset.location,
                'year_of_purchase': asset.year_of_purchase.isoformat(),
                'price': asset.price,
                'state': asset.state,
                'status': asset.status,
                'is_active': asset.is_active,
                'description': asset.description,
            }
        )
        try:
            self.save_old_asset_data(asset=asset)
        except ConnectionError as e:
            logger.error(f"[UpdateAsset GET] Redis connection error - {e}")
        return context

    def form_valid(self, form):
        updated_asset = form.save()
        try:
            self.create_asset_history(new_asset=updated_asset)
        except ConnectionError as e:
            logger.error(f"[UpdateAsset POST] Redis connection error - {e}")
        return HttpResponseRedirect(f'/assets/{self.get_object().pk}')

    def put(self, *args, **kwargs):
        super(UpdateAsset, self).put(*args, **kwargs)


class DeleteAssert(UserMixin, DeleteView):
    """ Удаление актива
    """
    model = Asset
    template_name = 'web/delete_asset.html'
    success_url = reverse_lazy('assets')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteAssert, self).get_context_data()
        try:
            asset = Asset.objects.get(pk=self.get_object().pk)
            context['asset'] = asset
        except Asset.DoesNotExist as e:
            logger.error(f"[DeleteAssert GET] Delete asset error - {e}")
            return {}
        context['title'] = f'Удаление актива {asset.name}'
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
        except Location.DoesNotExist as e:
            logger.error(f"[UpdateLocation GET] Update location error - {e}")
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
    template_name = 'web/delete_location.html'
    success_url = reverse_lazy('locations')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DeleteLocation, self).get_context_data()
        try:
            location = Location.objects.get(pk=self.get_object().pk)
            context['location'] = location
        except Asset.DoesNotExist as e:
            logger.error(f"[DeleteLocation GET] Delete location error - {e}")
            return {}
        context['title'] = f'Удаление склада {location.name}'
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
