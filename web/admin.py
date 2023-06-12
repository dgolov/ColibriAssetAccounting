from django.contrib import admin
from web.models import Asset, AssetImage, Location, Order, History, Notifications


admin.site.site_header = 'Административная панель'
admin.site.site_title = 'Административная панель'


@admin.register(Asset)
class AssetsAdmin(admin.ModelAdmin):
    """ Админ панель активов
    """
    list_display = ['id', 'name', 'location', 'updated_at', 'price', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['location__name', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']


@admin.register(AssetImage)
class AssetImageAdmin(admin.ModelAdmin):
    """ Админ панель изображений активов
    """
    list_display = ['id', 'asset', 'title']
    list_display_links = ['title', 'asset']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """ Админ панель складов
    """
    list_display = ['id', 'name', 'city', 'address']
    list_display_links = ['id', 'name']
    list_filter = ['city']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """ Админ панель отчетов
    """
    list_display = ['id', 'file', 'created_at']
    list_display_links = ['id', 'file']


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    """ Админ панель истории
    """
    list_display = ['id', 'event_name', 'full_name']
    list_display_links = ['event_name']

    def full_name(self, obj):
        return obj.__str__()

    full_name.short_description = 'Актив'


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    """ Админ панель уведомлений
    """
    list_display = ['id', 'message', 'level']
    list_display_links = ['message']
    list_filter = ['level']

