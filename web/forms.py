from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from web.models import Asset, AssetImage, Location, Order, History


class CreateAssetForm(forms.ModelForm):
    """ Форма регистрации нового актива
    """
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите номер договора...'}
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Введите комментарий менеджера...'}
        )
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    year_of_purchase = forms.DateField(
        widget=AdminDateWidget(
            attrs={'class': 'form-control', 'type': "date"}
        )
    )
    price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите комментарий менеджера...'}
        )
    )
    status = forms.CharField(
        widget=forms.Select(
            choices=Asset.STATUS_CHOICES,
            attrs={'class': 'form-control'}
        )
    )
    state = forms.CharField(
        widget=forms.Select(
            choices=Asset.STATE_CHOICES,
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = Asset
        fields = (
            'name', 'description', 'location', 'year_of_purchase', 'price', 'state', 'status'
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
            attrs={'class': 'form-control', 'placeholder': 'Введите номер договора...'}
        )
    )
    city = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите номер договора...'}
        )
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите номер договора...'}
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Введите комментарий менеджера...'}
        )
    )
