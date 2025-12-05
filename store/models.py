from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])
# store/models.py (Add this below the Category model)

class Product(models.Model):
    # Foreign Key links the Product to a Category
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE) 
    
    # Core Product Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # e.g., 1500.99
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        # index_together is removed in Django 5.0+. Use indexes instead:
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])
    
    # Jewelry Specific Fields
    metal_type = models.CharField(max_length=100) # Gold, Sterling Silver, Platinum
    gemstone = models.CharField(max_length=100, blank=True) # Diamond, Sapphire, Pearl
    weight_grams = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Inventory & Status
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True) # Requires Pillow
    is_available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])
# Create your models here.
