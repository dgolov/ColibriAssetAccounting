from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from excel import parse_import, handle_uploaded_file
from redis.exceptions import ConnectionError
from web.models import Asset, AssetImage, Location, Order, History, Notifications, CustomUser
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


class MainView(View, UserMixin):
    """ Представление дашборда
    """
    def get(self, *args, **kwargs):
        if not self.has_login(request=self.request):
            return HttpResponseRedirect('/auth')
        return render(self.request, "web/index.html", context=self.get_context_data())

    @staticmethod
    def get_context_data():
        return {
            "title": " Дашборд",
            "assets_count": Asset.objects.all().count(),
            "location_count": Location.objects.all().count(),
            "user_count": CustomUser.objects.all().count(),
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
                user = CustomUser.objects.get(email=username)
                username = user.username
            except CustomUser.DoesNotExist as e:
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
        return HttpResponseRedirect('/auth')


class Profile(View, UserMixin):
    """ Личный кабинет пользователя
    """
    def get(self, *args, **kwargs):
        if not self.has_login(request=self.request):
            return HttpResponseRedirect('/auth')

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
        if not self.has_login(request=self.request):
            return HttpResponseRedirect('/auth')

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


class Search(View):
    """ Поиск по активам и складам
    """
    ordering = 'name'
    ordering_desc = False

    def get(self, *args, **kwargs):
        sort_param = self.request.GET.get('sort')

        if 'desc' in self.request.GET:
            self.ordering_desc = not self.ordering_desc
        if sort_param:
            self.ordering = sort_param

        ordering = f'-{self.ordering}' if self.ordering_desc else f'{self.ordering}'

        search_query = self.request.GET.get('search', '')
        assets = Asset.objects.filter(name__icontains=search_query).order_by(ordering)
        locations = Location.objects.filter(name__icontains=search_query).order_by(ordering)
        return render(
            self.request,
            template_name='web/search.html',
            context={
                'assets': assets,
                'locations': locations,
            }
        )


class AssetList(UserMixin, ListView):
    """ Представление главной страницы (список активов)
    """
    model = Asset
    template_name = 'web/assets.html'
    context_object_name = 'assets'
    paginate_by = 30
    ordering = 'name'
    ordering_desc = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AssetList, self).get_context_data()

        asset_query = None
        search = self.request.GET.get('search')
        location_pk = self.request.GET.get('location')

        if location_pk:
            asset_query = Asset.objects.filter(
                location_id=location_pk,
                is_active=True,
                parent=None
            ).order_by('name')
        elif search:
            asset_query = Asset.objects.filter(
                    name__iregex=search,
                    is_active=True,
                    parent=None
                ).order_by('name')

        if asset_query and not self.request.user.is_superuser:
            asset_query.filter(location__in=self.request.user.locations.all())
            
        if asset_query:
            context['assets'] = asset_query

        context['title'] = 'Активы'
        
        if self.request.user.is_superuser:
            context['locations'] = Location.objects.all()
        else:
            context['locations'] = self.request.user.locations.all()
            
        return context

    def get_queryset(self):
        sort_param = self.request.GET.get('sort')
        if sort_param:
            self.ordering = sort_param
        ordering = f'-{self.ordering}' if self.ordering_desc else f'{self.ordering}'
        query = Asset.objects.filter(is_active=True, parent=None).order_by(ordering)
        if not self.request.user.is_superuser:
            query = query.filter(location__in=self.request.user.locations.all())
        return query

    def get(self, request, *args, **kwargs):
        if 'desc' in request.GET:
            self.ordering_desc = not self.ordering_desc
        return super().get(request, *args, **kwargs)


class AssetDetail(UserMixin, DetailView):
    """ Детальное представление актива
    """
    model = Asset
    template_name = 'web/asset_detail.html'
    context_object_name = 'asset'

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request) and self.get_object().location not in request.user.locations.all():
            return HttpResponseRedirect('/assets')
        return super(AssetDetail, self).get(request, *args, **kwargs)

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
        context['form'] = forms.CreateAssetForm(user=self.request.user)
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
            if not self.has_permission(request=self.request) and asset.location not in self.request.user.locations.all:
                logger.warning(
                    f"There are not enough permissions (User: {self.request.user}) to edit the asset - {asset}"
                )
                return {}
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

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request) and self.get_object().location not in request.user.locations.all():
            return HttpResponseRedirect('/assets')
        return super(DeleteAssertImage, self).get(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.has_permission(request=self.request):
            return HttpResponseRedirect('/locations')
        return super(DeleteAssertImage, self).post(*args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request) and self.get_object().location not in request.user.locations.all():
            return HttpResponseRedirect('/assets')
        return super(UpdateAsset, self).get(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        if not self.has_permission(request=self.request):
            return HttpResponseRedirect('/locations')
        return super(UpdateAsset, self).post(*args, **kwargs)

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
            object_id=self.get_object().pk,
            user=self.request.user,
            initial={
                'name': asset.name,
                'location': asset.location,
                'year_of_purchase': asset.year_of_purchase.isoformat(),
                'price': asset.price,
                'state': asset.state,
                'status': asset.status,
                'is_active': asset.is_active,
                'description': asset.description,
                'ozon_slug': asset.ozon_slug,
                'count': asset.count,
            }
        )
        try:
            self.save_old_asset_data(asset=asset)
        except ConnectionError as e:
            logger.error(f"[UpdateAsset GET] Redis connection error - {e}")
        except Exception as e:
            logger.error(f"[UpdateAsset GET] Save to redis error - {e}")
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


class CloneAssert(UserMixin, CreateView):
    """ Дублирование актива
    """
    model = Asset
    template_name = 'web/clone_asset.html'
    form_class = forms.CloneAssetForm

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CloneAssert, self).get_context_data()
        context['title'] = 'Дублирование актива'
        context['asset'] = self.get_object()
        return context
    
    def post(self, request, *args, **kwargs):
        logger.info(f"Cloning asset {self.get_object()}")
        try:
            asset = self.get_object()
            new_asset = Asset.objects.create(
                name=asset.name,
                description=asset.description,
                location=asset.location,
                year_of_purchase=asset.year_of_purchase,
                price=asset.price,
                state=asset.state,
                status=asset.status,
                is_active=asset.is_active,
                auto_update_price=asset.auto_update_price,
                ozon_slug=asset.ozon_slug,
                count=asset.count,
            )
            new_asset.images.add(*asset.images.all())
            new_asset.history.add(*asset.history.all())
            new_asset.save()
            History.objects.create(asset=new_asset, event_name="Дублирование актива")
            add_message(
                self.request,
                level='success', message=f'Актив {self.get_object()} успешно продублирован.'
            )
        except Exception as e:
            logger.error(f"Clone asset {self.get_object()} error - {e}")
            add_message(
                self.request,
                level='error',
                message=f"Ошибка дублирования актива {self.get_object()} - {e}"
            )
        return HttpResponseRedirect(f'/assets')


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
    ordering = 'name'
    ordering_desc = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LocationList, self).get_context_data()
        context['title'] = 'Склады'
        return context

    def get_queryset(self):
        sort_param = self.request.GET.get('sort')
        if sort_param == "assets_count":
            sort_param = "assets__count"
        if sort_param:
            self.ordering = sort_param
        ordering = f'-{self.ordering}' if self.ordering_desc else f'{self.ordering}'

        if self.has_permission(request=self.request):
            return Location.objects.all().order_by(ordering)
        else:
            return self.request.user.locations.all().order_by(ordering)

    def get(self, request, *args, **kwargs):
        if 'desc' in request.GET:
            self.ordering_desc = not self.ordering_desc
        return super().get(request, *args, **kwargs)


class LocationDetail(UserMixin, DetailView):
    """ Детальное представление локаций
    """
    model = Location
    template_name = 'web/location_detail.html'
    context_object_name = 'location'

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request) and self.get_object() not in self.request.user.locations.all():
            return HttpResponseRedirect('/locations')
        return super(LocationDetail, self).get(request, *args, **kwargs)

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
    
    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request):
            return HttpResponseRedirect('/locations')
        return super(CreateLocation, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        if not self.has_permission(request=request):
            return HttpResponseRedirect('/locations')
        return super(CreateLocation, self).post(request, *args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request):
            return HttpResponseRedirect('/locations')
        return super(UpdateLocation, self).get(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        if not self.has_permission(request=self.request):
            return HttpResponseRedirect('/locations')
        return super(UpdateLocation, self).post(*args, **kwargs)

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

    def get(self, request, *args, **kwargs):
        if not self.has_permission(request=request):
            return HttpResponseRedirect('/locations')
        return super(DeleteLocation, self).get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        if not self.has_permission(request=request):
            return HttpResponseRedirect('/locations')
        add_message(self.request, level='success', message=f'Склад {self.get_object()} успешно удален.')
        return super(DeleteLocation, self).delete(request, *args, **kwargs)

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

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.model.objects.filter(user=self.request.user)
        return super(OrderList, self).get_queryset()


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
