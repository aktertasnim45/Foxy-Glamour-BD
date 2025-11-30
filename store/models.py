from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True) # Used for clean URLs (e.g., /necklaces/)

    class Meta:
        verbose_name_plural = 'categories' # Fixes the pluralization in the admin panel

    def __str__(self):
        return self.name
# store/models.py (Add this below the Category model)

class Product(models.Model):
    # Foreign Key links the Product to a Category
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE) 
    
    # Core Product Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., 1500.99
    
    # Jewelry Specific Fields
    metal_type = models.CharField(max_length=100) # Gold, Sterling Silver, Platinum
    gemstone = models.CharField(max_length=100, blank=True) # Diamond, Sapphire, Pearl
    weight_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Inventory & Status
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True) # Requires Pillow
    is_available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
# Create your models here.
