from django import forms
from django.contrib.admin.widgets import AdminDateWidget
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
    asset = forms.ModelChoiceField(
        queryset=Asset.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        ),
        label="Актив"
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}
        ),
        label="Изображение"
    )

    class Meta:
        model = AssetImage
        fields = (
            'asset', 'image'
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
