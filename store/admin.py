from django.contrib import admin
from .models import Category, Product 

# Customizing the Admin interface for Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} 

# Customizing the Admin interface for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'is_available', 'created', 'updated']
    list_filter = ['is_available', 'created', 'updated', 'category']
    list_editable = ['price', 'is_available'] 
    prepopulated_fields = {'slug': ('name',)}
# Register your models here.
