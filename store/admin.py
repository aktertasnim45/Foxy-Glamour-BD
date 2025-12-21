from django.contrib import admin
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Category, Product, Size, Theme, HeroSection


# ==========================================
# PRODUCT IMPORT/EXPORT RESOURCE
# ==========================================
class ProductResource(resources.ModelResource):
    """Resource for importing/exporting products via CSV/Excel"""
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    sizes = fields.Field(
        column_name='sizes',
        attribute='sizes',
        widget=ManyToManyWidget(Size, separator=',', field='code')
    )
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'price', 'stock', 
                  'available', 'metal', 'gemstone', 'is_adjustable', 
                  'sizes', 'description')
        export_order = ('id', 'name', 'slug', 'category', 'price', 'stock',
                       'available', 'metal', 'gemstone', 'is_adjustable', 
                       'sizes', 'description')
        import_id_fields = ('id',)
        skip_unchanged = True
        report_skipped = True


# ==========================================
# CATEGORY IMPORT/EXPORT RESOURCE
# ==========================================
class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        import_id_fields = ('id',)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'primary_color', 'button_bg_color', 'buy_now_bg_color']
    list_editable = ['is_active', 'primary_color', 'button_bg_color', 'buy_now_bg_color']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'is_active')
        }),
        ('General Colors', {
            'fields': ('primary_color', 'text_color', 'bg_color', 'accent_color', 'promo_bg')
        }),
        ('Primary Button (Add to Cart)', {
            'fields': ('button_bg_color', 'button_text_color', 'button_hover_bg_color')
        }),
        ('Secondary Button (Buy Now)', {
            'fields': ('buy_now_bg_color', 'buy_now_text_color', 'buy_now_hover_bg_color', 'buy_now_hover_text_color')
        }),
    )


# Customizing the Admin interface for Category with Import/Export
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} 


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


# Customizing the Admin interface for Product with Import/Export
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ['name', 'slug', 'price', 'discount_percentage', 'discount_amount', 'stock', 'available', 'is_adjustable', 'created', 'updated']
    list_filter = ['available', 'is_adjustable', 'created', 'updated', 'category', 'metal']
    list_editable = ['price', 'discount_percentage', 'discount_amount', 'stock', 'available', 'is_adjustable'] 
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('sizes',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'image', 'description')
        }),
        ('Pricing & Discount', {
            'fields': ('price', 'discount_percentage', 'discount_amount'),
            'description': 'Set discount percentage (0-100) OR fixed amount. Percentage takes priority.'
        }),
        ('Inventory', {
            'fields': ('available', 'stock')
        }),
        ('Jewelry Details', {
            'fields': ('metal', 'gemstone', 'is_adjustable', 'sizes')
        }),
    )
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


# ==========================================
# HERO SECTION ADMIN
# ==========================================
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    """
    World-class admin interface for managing the hero section.
    Includes preview functionality for images and videos.
    """
    list_display = ['name', 'is_active', 'background_type', 'background_preview', 'show_logo', 'show_tagline', 'updated']
    list_filter = ['is_active', 'background_type', 'show_logo', 'show_headline', 'show_tagline']
    list_editable = ['is_active']
    search_fields = ['name', 'headline', 'tagline']
    readonly_fields = ['background_preview_large', 'logo_preview', 'created', 'updated']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('name', 'is_active'),
            'description': 'Give this configuration a name. Only one hero can be active at a time.'
        }),
        ('Background', {
            'fields': ('background_type', 'background_image', 'background_video', 'background_preview_large', 'enable_ken_burns'),
            'description': 'Choose between image or video. For video, upload MP4 or WEBM (keep under 10MB).'
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview', 'show_logo'),
            'description': 'Upload your logo (SVG recommended for best quality).'
        }),
        ('Text Content', {
            'fields': ('headline', 'show_headline', 'tagline', 'show_tagline'),
            'description': 'Customize the text displayed in the hero section.'
        }),
        ('Timestamps', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def background_preview(self, obj):
        """Small thumbnail preview for list view."""
        if obj.background_type == 'image' and obj.background_image:
            return format_html(
                '<img src="{}" style="max-width: 80px; max-height: 50px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"/>',
                obj.background_image.url
            )
        elif obj.background_type == 'video' and obj.background_video:
            return format_html(
                '<span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4px 8px; border-radius: 4px; font-size: 10px;">🎥 VIDEO</span>'
            )
        return format_html('<span style="color: #999;">No media</span>')
    background_preview.short_description = 'Preview'
    
    def background_preview_large(self, obj):
        """Large preview for change form."""
        if obj.background_type == 'image' and obj.background_image:
            return format_html(
                '<div style="margin: 10px 0;"><img src="{}" style="max-width: 400px; max-height: 250px; object-fit: cover; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"/></div>',
                obj.background_image.url
            )
        elif obj.background_type == 'video' and obj.background_video:
            return format_html(
                '<div style="margin: 10px 0;"><video src="{}" style="max-width: 400px; max-height: 250px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" controls muted></video></div>',
                obj.background_video.url
            )
        return format_html('<span style="color: #999; font-style: italic;">No background uploaded yet</span>')
    background_preview_large.short_description = 'Background Preview'
    
    def logo_preview(self, obj):
        """Logo preview for change form."""
        if obj.logo:
            return format_html(
                '<div style="margin: 10px 0; background: #333; padding: 20px; border-radius: 8px; display: inline-block;"><img src="{}" style="max-width: 200px; max-height: 80px;"/></div>',
                obj.logo.url
            )
        return format_html('<span style="color: #999; font-style: italic;">No logo uploaded. Will use default logo.</span>')
    logo_preview.short_description = 'Logo Preview'
    
    actions = ['make_active']
    
    @admin.action(description='Set selected hero as active')
    def make_active(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(request, "Only one hero can be active at a time. Please select only one.", level='error')
            return
        # Deactivate all others
        HeroSection.objects.update(is_active=False)
        # Activate selected
        queryset.update(is_active=True)
        self.message_user(request, f"'{queryset.first().name}' is now the active hero section.")
