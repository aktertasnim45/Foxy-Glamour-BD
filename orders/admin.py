from django.contrib import admin
from django.contrib import messages
from .models import Order, OrderItem, PathaoCity, PathaoZone, PathaoArea


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


def send_to_pathao(modeladmin, request, queryset):
    """Admin action to send selected orders to Pathao"""
    from .pathao import PathaoClient
    
    client = PathaoClient()
    success_count = 0
    error_count = 0
    
    for order in queryset:
        if order.sent_to_pathao:
            messages.warning(request, f"Order #{order.id} was already sent to Pathao")
            continue
            
        try:
            result = client.create_parcel(order)
            if result.get('type') == 'success':
                success_count += 1
            else:
                error_count += 1
                messages.error(request, f"Order #{order.id}: {result.get('message', 'Unknown error')}")
        except Exception as e:
            error_count += 1
            messages.error(request, f"Order #{order.id}: {str(e)}")
    
    if success_count:
        messages.success(request, f"Successfully sent {success_count} order(s) to Pathao")
    if error_count:
        messages.warning(request, f"Failed to send {error_count} order(s)")

send_to_pathao.short_description = "Send selected orders to Pathao Courier"


def update_pathao_status(modeladmin, request, queryset):
    """Admin action to update Pathao status for selected orders"""
    from .pathao import PathaoClient
    
    client = PathaoClient()
    updated_count = 0
    
    for order in queryset.filter(sent_to_pathao=True, pathao_consignment_id__isnull=False):
        try:
            result = client.get_order_status(order.pathao_consignment_id)
            if result:
                data = result.get('data', {})
                order.pathao_order_status = data.get('order_status', order.pathao_order_status)
                order.save()
                updated_count += 1
        except Exception as e:
            messages.error(request, f"Order #{order.id}: {str(e)}")
    
    messages.success(request, f"Updated status for {updated_count} order(s)")

update_pathao_status.short_description = "Update Pathao status for selected orders"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone',
                    'address', 'city', 'payment_method', 'paid', 'status',
                    'sent_to_pathao', 'pathao_consignment_id', 'created']
    list_filter = ['paid', 'status', 'sent_to_pathao', 'created', 'updated']
    list_editable = ['paid', 'status']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'pathao_consignment_id']
    inlines = [OrderItemInline]
    actions = [send_to_pathao, update_pathao_status]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'postal_code', 'city', 'shipping_zone')
        }),
        ('Payment', {
            'fields': ('payment_method', 'bkash_number', 'transaction_id', 'paid')
        }),
        ('Order Status', {
            'fields': ('status',)
        }),
        ('Pathao Courier', {
            'fields': ('sent_to_pathao', 'pathao_consignment_id', 'pathao_order_status',
                      'pathao_city_id', 'pathao_zone_id', 'pathao_area_id'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['pathao_consignment_id', 'pathao_order_status']


# Pathao Location Admin
def sync_pathao_cities(modeladmin, request, queryset):
    """Sync cities from Pathao API"""
    from .pathao import PathaoClient
    
    client = PathaoClient()
    try:
        cities = client.get_cities()
        created = 0
        updated = 0
        for city_data in cities:
            city, was_created = PathaoCity.objects.update_or_create(
                city_id=city_data.get('city_id'),
                defaults={'city_name': city_data.get('city_name', '')}
            )
            if was_created:
                created += 1
            else:
                updated += 1
        messages.success(request, f"Synced {created} new cities, updated {updated}")
    except Exception as e:
        messages.error(request, f"Failed to sync cities: {str(e)}")

sync_pathao_cities.short_description = "Sync all cities from Pathao API"


def sync_zones_for_city(modeladmin, request, queryset):
    """Sync zones for selected cities"""
    from .pathao import PathaoClient
    
    client = PathaoClient()
    total_created = 0
    total_updated = 0
    
    for city in queryset:
        try:
            zones = client.get_zones(city.city_id)
            for zone_data in zones:
                zone, was_created = PathaoZone.objects.update_or_create(
                    zone_id=zone_data.get('zone_id'),
                    defaults={
                        'zone_name': zone_data.get('zone_name', ''),
                        'city': city
                    }
                )
                if was_created:
                    total_created += 1
                else:
                    total_updated += 1
        except Exception as e:
            messages.error(request, f"Failed to sync zones for {city.city_name}: {str(e)}")
    
    messages.success(request, f"Synced {total_created} new zones, updated {total_updated}")

sync_zones_for_city.short_description = "Sync zones for selected cities"


@admin.register(PathaoCity)
class PathaoCityAdmin(admin.ModelAdmin):
    list_display = ['city_id', 'city_name', 'is_active', 'zone_count']
    list_filter = ['is_active']
    search_fields = ['city_name']
    actions = [sync_pathao_cities, sync_zones_for_city]
    
    def zone_count(self, obj):
        return obj.zones.count()
    zone_count.short_description = 'Zones'


@admin.register(PathaoZone)
class PathaoZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_id', 'zone_name', 'city', 'is_active']
    list_filter = ['city', 'is_active']
    search_fields = ['zone_name', 'city__city_name']
    raw_id_fields = ['city']


@admin.register(PathaoArea)
class PathaoAreaAdmin(admin.ModelAdmin):
    list_display = ['area_id', 'area_name', 'zone', 'is_active']
    list_filter = ['zone__city', 'is_active']
    search_fields = ['area_name', 'zone__zone_name']
    raw_id_fields = ['zone']
