from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])


class Size(models.Model):
    name = models.CharField(max_length=20) # e.g. "US 7", "Small"
    code = models.SlugField(max_length=20, unique=True) # e.g. "7", "s"

    class Meta:
        ordering = ('code',)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Jewelry Specifics
    metal = models.CharField(max_length=100, choices=[
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Platinum', 'Platinum'),
        ('Rose Gold', 'Rose Gold'),
        ('Brass', 'Brass')
    ], blank=True)
    
    gemstone = models.CharField(max_length=100, blank=True) # e.g. Diamond, Ruby, Sapphire
    
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    is_adjustable = models.BooleanField(default=False, verbose_name="Is Adjustable Ring")
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Discount Fields
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percentage discount (0-100). Takes priority over fixed amount."
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Fixed discount amount in TK"
    )

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])

    @property
    def has_discount(self):
        """Check if product has any active discount."""
        return bool(self.discount_percentage or self.discount_amount)

    @property
    def discounted_price(self):
        """Calculate price after applying discount."""
        from decimal import Decimal
        if self.discount_percentage:
            discount = self.price * (self.discount_percentage / Decimal('100'))
            return round(self.price - discount, 2)
        elif self.discount_amount:
            return max(self.price - self.discount_amount, Decimal('0'))
        return self.price


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Theme(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    
    # CSS Variable Mapping
    primary_color = models.CharField(max_length=7, default='#000000', help_text="Main brand color (Buttons, Prices)")
    text_color = models.CharField(max_length=7, default='#171717', help_text="Body text color")
    bg_color = models.CharField(max_length=7, default='#ffffff', help_text="Page background color")
    accent_color = models.CharField(max_length=7, default='#D4AF37', help_text="Highlights, links hover")
    promo_bg = models.CharField(max_length=7, default='#452829', help_text="Promo bar background")
   
    # Button Colors
    button_bg_color = models.CharField(max_length=7, default='#000000', help_text="Button background color (Add to Cart)")
    button_text_color = models.CharField(max_length=7, default='#ffffff', help_text="Button text color")
    button_hover_bg_color = models.CharField(max_length=7, default='#333333', help_text="Button hover background color")
    
    # Secondary Button (Buy Now)
    buy_now_bg_color = models.CharField(max_length=7, default='#ffffff', help_text="Buy Now background color")
    buy_now_text_color = models.CharField(max_length=7, default='#000000', help_text="Buy Now text color")
    buy_now_hover_bg_color = models.CharField(max_length=7, default='#000000', help_text="Buy Now hover background color")
    buy_now_hover_text_color = models.CharField(max_length=7, default='#ffffff', help_text="Buy Now hover text color")

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'

    def save(self, *args, **kwargs):
        # Ensure only one theme is active at a time
        if self.is_active:
            Theme.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class HeroSection(models.Model):
    """
    Admin-manageable hero section for the homepage.
    Supports image or video backgrounds with customizable text and logo.
    Only one hero can be active at a time (singleton pattern).
    """
    BACKGROUND_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    name = models.CharField(max_length=100, help_text="Internal name for this configuration")
    is_active = models.BooleanField(default=False, help_text="Only one hero can be active at a time")
    
    # Background
    background_type = models.CharField(
        max_length=10, 
        choices=BACKGROUND_CHOICES, 
        default='image',
        help_text="Choose between image or video background"
    )
    background_image = models.ImageField(
        upload_to='hero/', 
        blank=True, 
        null=True,
        help_text="Upload an image (PNG, JPG, GIF). Recommended: 1920x1080 or higher"
    )
    background_video = models.FileField(
        upload_to='hero/videos/', 
        blank=True, 
        null=True,
        help_text="Upload a video (MP4, WEBM). Keep under 10MB for best performance"
    )
    
    # Logo
    logo = models.FileField(
        upload_to='hero/logos/', 
        blank=True, 
        null=True, 
        help_text="Upload SVG or image logo for hero section"
    )
    
    # Text Content
    headline = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional main headline text"
    )
    tagline = models.CharField(
        max_length=300, 
        blank=True, 
        default="Every Piece of Jewelry has a story to tell",
        help_text="Subtitle text below the logo"
    )
    
    # Display Settings
    show_logo = models.BooleanField(default=True, help_text="Show the logo in hero section")
    show_headline = models.BooleanField(default=False, help_text="Show the headline text")
    show_tagline = models.BooleanField(default=True, help_text="Show the tagline text")
    
    # Animation Settings
    enable_ken_burns = models.BooleanField(
        default=True, 
        help_text="Enable Ken Burns zoom animation for image backgrounds"
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hero Section'
        verbose_name_plural = 'Hero Sections'
        ordering = ['-is_active', '-updated']

    def save(self, *args, **kwargs):
        # Ensure only one hero is active at a time (singleton pattern)
        if self.is_active:
            HeroSection.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "✓ Active" if self.is_active else "Inactive"
        return f"{self.name} ({status})"
