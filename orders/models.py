from django.db import models
from django.contrib.auth.models import User
from store.models import Product

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ]
    
    # Discount for mobile payments (bKash/Nagad)
    MOBILE_PAYMENT_DISCOUNT = 10

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=11, help_text="11-digit mobile number", default='')
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    
    # NEW PAYMENT FIELDS
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    bkash_number = models.CharField(max_length=11, blank=True, null=True, help_text="The number you sent money from (bKash/Nagad)")
    transaction_id = models.CharField(max_length=30, blank=True, null=True, help_text="Transaction ID from bKash/Nagad")
    payment_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount for mobile payment methods")
    
    # SHIPPING
    SHIPPING_ZONE_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka (80 TK)'),
        ('intercity_dhaka', 'Intercity Dhaka (120 TK)'),
        ('outside_dhaka', 'Outside Dhaka (150 TK)'),
    ]
    shipping_zone = models.CharField(max_length=20, choices=SHIPPING_ZONE_CHOICES, default='inside_dhaka')

    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    # Pathao Courier Integration
    pathao_consignment_id = models.CharField(max_length=50, blank=True, null=True, 
        help_text="Pathao tracking/consignment ID")
    pathao_order_status = models.CharField(max_length=50, blank=True, null=True,
        help_text="Order status from Pathao")
    pathao_city_id = models.IntegerField(blank=True, null=True,
        help_text="Pathao City ID for delivery")
    pathao_zone_id = models.IntegerField(blank=True, null=True,
        help_text="Pathao Zone ID for delivery")
    pathao_area_id = models.IntegerField(blank=True, null=True,
        help_text="Pathao Area ID for delivery")
    sent_to_pathao = models.BooleanField(default=False,
        help_text="Whether this order has been sent to Pathao")

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Order {self.id}'
        
    def get_shipping_cost(self):
        if self.shipping_zone == 'outside_dhaka':
            return 150
        elif self.shipping_zone == 'intercity_dhaka':
            return 120
        else: # inside_dhaka
            return 80

    def get_total_cost(self):
        subtotal = sum(item.get_cost() for item in self.items.all())
        return subtotal + self.get_shipping_cost() - self.payment_discount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


# Pathao Location Models - for storing city/zone/area data
class PathaoCity(models.Model):
    """Stores Pathao city data synced from API"""
    city_id = models.IntegerField(unique=True, primary_key=True)
    city_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Pathao City"
        verbose_name_plural = "Pathao Cities"
        ordering = ['city_name']
    
    def __str__(self):
        return f"{self.city_name} (ID: {self.city_id})"


class PathaoZone(models.Model):
    """Stores Pathao zone data synced from API"""
    zone_id = models.IntegerField(unique=True, primary_key=True)
    zone_name = models.CharField(max_length=100)
    city = models.ForeignKey(PathaoCity, on_delete=models.CASCADE, related_name='zones')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Pathao Zone"
        verbose_name_plural = "Pathao Zones"
        ordering = ['zone_name']
    
    def __str__(self):
        return f"{self.zone_name} - {self.city.city_name} (ID: {self.zone_id})"


class PathaoArea(models.Model):
    """Stores Pathao area data synced from API"""
    area_id = models.IntegerField(unique=True, primary_key=True)
    area_name = models.CharField(max_length=100)
    zone = models.ForeignKey(PathaoZone, on_delete=models.CASCADE, related_name='areas')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Pathao Area"
        verbose_name_plural = "Pathao Areas"
        ordering = ['area_name']
    
    def __str__(self):
        return f"{self.area_name} - {self.zone.zone_name} (ID: {self.area_id})"