from django.contrib import admin
from web.models import Asset, AssetImage, Location, Order, History


admin.site.site_header = 'Административная панель'
admin.site.site_title = 'Административная панель'


@admin.register(Asset)
class AssetsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'updated_at', 'price', 'is_active']
    list_display_links = ['id', 'name']
    list_filter = ['name', 'location', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']


@admin.register(AssetImage)
class AssetImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'asset']
    list_display_links = ['id', 'asset']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city', 'address']
    list_display_links = ['id', 'name']
    list_filter = ['name', 'city']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'file', 'created_at']
    list_display_links = ['id', 'file']


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name']
    list_display_links = ['id']

    def full_name(self, obj):
        return obj.__str__()

    full_name.short_description = 'Актив'
