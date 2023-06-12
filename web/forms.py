from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User

from web.models import Asset, AssetImage, Location, Order, History


class AuthForm(forms.Form):
    """ Форма входа пользователя
    """
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите логин или email'}
        )
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}
        )
    )


class CreateAssetForm(forms.ModelForm):
    """ Форма регистрации нового актива
    """
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите название актива'}
        ),
        label="Название"
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Введите описание актива.'}
        ),
        label="Описание"
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        required=False,
        label="Склад"
    )
    year_of_purchase = forms.DateField(
        widget=AdminDateWidget(
            attrs={'class': 'form-control', 'type': "date"}
        ),
        label="Дата закупки"
    )
    price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите цену актива'}
        ),
        label="Стоимость"
    )
    status = forms.CharField(
        widget=forms.Select(
            choices=Asset.STATUS_CHOICES,
            attrs={'class': 'form-control'}
        ),
        label="Статсус"
    )
    state = forms.CharField(
        widget=forms.Select(
            choices=Asset.STATE_CHOICES,
            attrs={'class': 'form-control'}
        ),
        label="Состояние"
    )

    class Meta:
        model = Asset
        fields = (
            'name', 'description', 'location', 'year_of_purchase', 'price', 'state', 'status'
        )


class CreateAssetImageForm(forms.ModelForm):
    """ Форма добавления изображения к активу
    """
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите название актива'}
        ),
        label="Описание",
        required=False
    )
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        label="Актив",
        required=True
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        ),
        label="Изображение",
        required=True
    )

    class Meta:
        model = AssetImage
        fields = (
            'title', 'asset', 'image'
        )


class UpdateAssetForm(CreateAssetForm):
    """ Форма обновления актива
    """
    is_active = forms.BooleanField(required=False)

    class Meta:
        model = Asset
        fields = (
            'name', 'description', 'location', 'year_of_purchase', 'price', 'state', 'status', 'is_active'
        )


class LocationForm(forms.ModelForm):
    """ Форма создания и обновления локаций
    """
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите название склада'}
        ),
        label="Название"
    )
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите город'}
        ),
        label="Город"
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите адресс склада'}
        ),
        label="Адресс"
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите номер телефона склада'}
        ),
        label="Номер телефона"
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Введите описание склада'}
        ),
        label="Описание",
    )

    class Meta:
        model = Location
        fields = (
            'name', 'city', 'address', 'phone', 'description'
        )


class ProfileForm(forms.ModelForm):
    """ Форма редактирования данных пользователя для личного кабинета
    """
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите имя'}
        ),
        label="Имя",
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}
        ),
        label="Фамилия",
    )
    email = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите адрес электронной почты'}
        ),
        label="Электринная почта",
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
        label="Пароль",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']


class ImportAssetsForm(forms.Form):
    """ Форма иморта активов
    """
    file = forms.FileField()
