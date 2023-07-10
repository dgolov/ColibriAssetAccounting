from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from excel import parse_import, handle_uploaded_file
from redis.exceptions import ConnectionError
from web.models import Asset, AssetImage, Location, Order, History, Notifications
from web import forms
from web.mixins import UserMixin, AssetMixin, OrderMixin


import logging


logger = logging.getLogger('main')


def add_message(request, level, message):
    level_map = {
        "success": messages.SUCCESS,
        "error": messages.ERROR,
        "warning": messages.WARNING,
        "info": messages.INFO,
        "debug": messages.DEBUG
    }
    message_level = level_map.get(level)
    messages.add_message(request, message_level, message)
    Notifications.objects.create(message=message, level=level, user=request.user)


class MainView(View):
    """ Представление дашборда
    """
    def get(self, *args, **kwargs):
        return render(self.request, "web/index.html", context=self.get_context_data())

    @staticmethod
    def get_context_data():
        return {
            "title": " Дашборд",
            "assets_count": Asset.objects.all().count(),
            "location_count": Location.objects.all().count(),
            "user_count": User.objects.all().count(),
        }


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
            add_message(self.request, level='success', message=f"Данные пользователя обновлены")
        else:
            add_message(self.request, level='success', message=f"Ошибка! Данные пользователя не были обновлены.")
        return HttpResponseRedirect('/')


class AssetList(UserMixin, ListView):
    """ Представление главной страницы (список активов)
    """
    model = Asset
    template_name = 'web/assets.html'
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
        logger.info(f"[CreateAssert] Create asset successfully: {form.data}")
        History.objects.create(asset=asset, event_name="Создание актива")
        add_message(self.request, level='success', message=f"Актив {form.data.get('name')} успешно создан")
        return HttpResponseRedirect('/assets')

    def form_invalid(self, form):
        logger.warning(f"[CreateAssert] Invalid form data: {form.data}")
        add_message(
            self.request,
            level='error',
            message=f"Ошибка создания актива. {form.data.get('name')} Введены некорректные данные."
        )
        return HttpResponseRedirect('/assets')


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
        logger.info(f"Upload asset image for asset id {self._object_pk} successfully")
        return HttpResponseRedirect(f'/assets/{self._object_pk}')

    def form_invalid(self, form):
        logger.warning(f"Upload asset image for asset id {self._object_pk} error")
        add_message(
            self.request,
            level='error',
            message='Ошибка загрузки изображения актива. Введены некорректные данные.'
        )
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
            add_message(
                self.request,
                level='error',
                message='Ошибка записи истории актива. Нет соединения с брокером сообщений'
            )
        add_message(self.request, level='success', message=f"Актив {form.data.get('name')} успешно обновлен.")
        return HttpResponseRedirect(f'/assets/{self.get_object().pk}')

    def form_invalid(self, form):
        logger.warning(f"Update asset {form.data.get('name')} error")
        add_message(
            self.request,
            level='error',
            message=f"Ошибка обновления актива {form.data.get('name')}. Введены некорректные данные."
        )
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
            add_message(self.request, level='error', message=f'Ошибка удаления актива {self.get_object()} - {e}.')
            return {}
        context['title'] = f'Удаление актива {asset.name}'
        return context

    def delete(self, request, *args, **kwargs):
        add_message(self.request, level='success', message=f'Актив {self.get_object()} успешно удален.')
        return super(DeleteAssert, self).delete(request, *args, **kwargs)


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

    def form_valid(self, form):
        add_message(self.request, level='success', message=f"Склад {form.data.get('name')} успешно создан.")
        return super(CreateLocation, self).form_valid(form)

    def form_invalid(self, form):
        add_message(
            self.request,
            level='error',
            message=f"Ошибка создания склада {form.data.get('name')}. Введены некорректные данные."
        )
        return super(CreateLocation, self).form_invalid(form)


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

    def form_valid(self, form):
        add_message(self.request, level='success', message=f"Склад {form.data.get('name')} успешно обновлен.")
        return super(UpdateLocation, self).form_valid(form)

    def form_invalid(self, form):
        add_message(
            self.request,
            level='error',
            message=f"Ошибка обновления склада {form.data.get('name')}. Введены некорректные данные."
        )
        return super(UpdateLocation, self).form_invalid(form)


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

    def delete(self, request, *args, **kwargs):
        add_message(self.request, level='success', message=f'Склад {self.get_object()} успешно удален.')
        return super(DeleteLocation, self).delete(request, *args, **kwargs)


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


class CreateOrder(UserMixin, OrderMixin, View):
    """ Формировпние и загрузка отчета
    """
    template_name = 'web/create_order.html'

    @staticmethod
    def get_context_data():
        locations = Location.objects.all()
        return {
            'title': 'Создание отчета',
            'locations': locations
        }

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.get_context_data())

    def post(self, *args, **kwargs):
        self.parse_request_data(request=self.request)
        return HttpResponseRedirect('/orders')


class AssetsImport(UserMixin, View):
    """ Импорт активов средствами excel
    """
    template_name = 'web/assets_import.html'

    def get(self, *args, **kwargs):
        return render(self.request, self.template_name, self.get_context_data())

    def post(self, *args, **kwargs):
        form = forms.ImportAssetsForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            path = handle_uploaded_file(self.request.FILES["file"])
            parse_messages = parse_import(file_name=path)
            error_messages_list = parse_messages.get('error')
            success_messages_list = parse_messages.get('success')
            if len(error_messages_list):
                for error_message in error_messages_list:
                    add_message(self.request, level='error', message=error_message)
            if len(success_messages_list):
                for success_message in success_messages_list:
                    add_message(self.request, level='success', message=success_message)
            return HttpResponseRedirect('/assets')
        return render(self.request, self.template_name, self.get_context_data())

    @staticmethod
    def get_context_data():
        return {
            "form": forms.ImportAssetsForm,
            "title": "Импорт активов"
        }


class NotificationsListView(UserMixin, ListView):
    """ Представление списка уведомлений
    """
    model = Notifications
    template_name = 'web/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(NotificationsListView, self).get_context_data()
        context['title'] = 'Уведомления'
        return context
