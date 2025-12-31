# Orders Module

> Order management, checkout flow, payment handling, and courier integration.

## Overview

The `orders` app handles:
- Order creation and management
- Multiple payment methods (COD, bKash, Nagad)
- Shipping zone calculations
- Pathao Courier API integration
- Telegram order notifications

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `models.py` | Order, OrderItem, Pathao location models | 141 |
| `views.py` | Checkout flow | 56 |
| `forms.py` | OrderCreateForm with validation | ~80 |
| `admin.py` | Order admin with Pathao integration | ~150 |
| `pathao.py` | Pathao Courier API client | 234 |
| `telegram.py` | Telegram notification service | 87 |
| `urls.py` | URL patterns | ~10 |

---

## Models

### Order

Main order model with customer information, payment, and shipping.

```python
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
    ]

    SHIPPING_ZONE_CHOICES = [
        ('inside_dhaka', 'Inside Dhaka (80 TK)'),
        ('intercity_dhaka', 'Intercity Dhaka (120 TK)'),
        ('outside_dhaka', 'Outside Dhaka (150 TK)'),
    ]

    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    # Customer Info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    
    # Payment
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    bkash_number = models.CharField(max_length=11, blank=True, null=True)
    transaction_id = models.CharField(max_length=30, blank=True, null=True)
    
    # Shipping
    shipping_zone = models.CharField(max_length=20, choices=SHIPPING_ZONE_CHOICES, default='inside_dhaka')
    
    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    paid = models.BooleanField(default=False)
    
    # Pathao Integration
    pathao_consignment_id = models.CharField(max_length=50, blank=True, null=True)
    pathao_order_status = models.CharField(max_length=50, blank=True, null=True)
    pathao_city_id = models.IntegerField(blank=True, null=True)
    pathao_zone_id = models.IntegerField(blank=True, null=True)
    pathao_area_id = models.IntegerField(blank=True, null=True)
    sent_to_pathao = models.BooleanField(default=False)
    
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
```

**Methods:**

```python
def get_shipping_cost(self):
    if self.shipping_zone == 'outside_dhaka':
        return 150
    elif self.shipping_zone == 'intercity_dhaka':
        return 120
    else:  # inside_dhaka
        return 80

def get_total_cost(self):
    return sum(item.get_cost() for item in self.items.all()) + self.get_shipping_cost()
```

---

### OrderItem

Individual line items within an order.

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot at purchase
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Cost snapshot
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity
```

**Important:** `price` and `cost_price` are snapshots at purchase time, not references to current product prices.

---

### Pathao Location Models

Cached location data from Pathao API.

```python
class PathaoCity(models.Model):
    city_id = models.IntegerField(unique=True, primary_key=True)
    city_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class PathaoZone(models.Model):
    zone_id = models.IntegerField(unique=True, primary_key=True)
    zone_name = models.CharField(max_length=100)
    city = models.ForeignKey(PathaoCity, on_delete=models.CASCADE, related_name='zones')

class PathaoArea(models.Model):
    area_id = models.IntegerField(unique=True, primary_key=True)
    area_name = models.CharField(max_length=100)
    zone = models.ForeignKey(PathaoZone, on_delete=models.CASCADE, related_name='areas')
```

---

## Views

### order_create

Main checkout view handling both GET (form display) and POST (order submission).

```python
def order_create(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # Attach user if logged in
            if request.user.is_authenticated:
                order.user = request.user
            
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    cost_price=item['product'].cost_price,  # Snapshot cost
                    quantity=item['quantity']
                )
                
                # Decrement stock
                product = item['product']
                product.stock = max(product.stock - item['quantity'], 0)
                product.save()
            
            # Send Telegram notification
            try:
                send_order_notification(order)
            except Exception:
                pass  # Don't fail order if notification fails
            
            # Clear cart
            cart.clear()
            
            return render(request, 'orders/order/created.html', {'order': order})
    else:
        # Pre-fill form for logged-in users
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})
```

---

## Pathao API Integration

### PathaoClient Class

```python
class PathaoClient:
    TOKEN_CACHE_KEY = 'pathao_access_token'
    TOKEN_CACHE_TIMEOUT = 3600  # 1 hour

    def __init__(self):
        self.base_url = settings.PATHAO_BASE_URL
        self.client_id = settings.PATHAO_CLIENT_ID
        self.client_secret = settings.PATHAO_CLIENT_SECRET
        self.client_email = settings.PATHAO_CLIENT_EMAIL
        self.client_password = settings.PATHAO_CLIENT_PASSWORD
        self.store_id = settings.PATHAO_STORE_ID
```

**Methods:**

#### _get_token()
Fetches or retrieves cached access token.
```python
def _get_token(self):
    token = cache.get(self.TOKEN_CACHE_KEY)
    if token:
        return token
    
    # Request new token
    response = requests.post(f"{self.base_url}/aladdin/api/v1/issue-token", json={
        'client_id': self.client_id,
        'client_secret': self.client_secret,
        'username': self.client_email,
        'password': self.client_password,
        'grant_type': 'password'
    })
    
    token = response.json().get('access_token')
    cache.set(self.TOKEN_CACHE_KEY, token, expires_in - 60)
    return token
```

#### get_cities(), get_zones(), get_areas()
Fetch location data from Pathao API.

#### create_parcel()
Create a delivery order in Pathao.

```python
def create_parcel(self, order):
    payload = {
        'store_id': int(self.store_id),
        'merchant_order_id': str(order.id),
        'sender_name': settings.PATHAO_SENDER_NAME,
        'sender_phone': settings.PATHAO_SENDER_PHONE,
        'recipient_name': f"{order.first_name} {order.last_name}".strip(),
        'recipient_phone': order.phone,
        'recipient_address': order.address,
        'recipient_city': order.pathao_city_id or 1,
        'recipient_zone': order.pathao_zone_id or 1,
        'recipient_area': order.pathao_area_id or 1,
        'delivery_type': 48,  # Normal delivery
        'item_type': 2,  # Parcel
        'amount_to_collect': float(order.get_total_cost()) if order.payment_method == 'cod' else 0,
        'item_description': items_description,
    }
    
    response = requests.post(f"{self.base_url}/aladdin/api/v1/orders", json=payload, headers=headers)
    
    # Update order with Pathao response
    order.pathao_consignment_id = response.json()['data']['consignment_id']
    order.sent_to_pathao = True
    order.save()
```

---

## Telegram Notifications

### send_telegram_message()

```python
def send_telegram_message(message):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    if not bot_token or not chat_id:
        return False
    
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    })
```

### send_order_notification()

Sends formatted order details to Telegram.

```python
def send_order_notification(order):
    items_text = ""
    for item in order.items.all():
        items_text += f"  • {item.product.name} x{item.quantity} = ৳{item.get_cost()}\n"
    
    message = f"""
🛒 <b>New Order #{order.id}</b>

👤 <b>Customer:</b>
{order.first_name} {order.last_name}
📞 {order.phone}
{"📧 " + order.email if order.email else ""}

📍 <b>Address:</b>
{order.address}
{order.city}, {order.postal_code}
🚚 {order.get_shipping_zone_display()}

📦 <b>Items:</b>
{items_text}
💰 <b>Subtotal:</b> ৳{subtotal}
🚚 <b>Shipping:</b> ৳{order.get_shipping_cost()}
💵 <b>Total:</b> ৳{order.get_total_cost()}

💳 <b>Payment:</b> {order.get_payment_method_display()}
{"🔢 TxID: " + order.transaction_id if order.transaction_id else ""}

⏰ {order.created.strftime('%d %b %Y, %I:%M %p')}
"""
    
    return send_telegram_message(message.strip())
```

---

## Admin Configuration

### OrderAdmin

- List display with order details, status, Pathao integration
- Custom actions for sending to Pathao
- Inline display of OrderItems
- Filters by status, payment method, shipping zone

---

## Order Flow

```
1. User clicks "Checkout"
2. GET /orders/create/ - Display form
3. User fills form, selects payment method
4. POST /orders/create/ - Validate and create order
5. Create OrderItem for each cart item
6. Snapshot price and cost_price
7. Decrement product stock
8. Send Telegram notification
9. Clear cart
10. Display success page
```

---

## URL Patterns

```python
app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
]
```

---

## Integration Points

### With Cart App
- Imports `Cart` class
- Iterates cart items to create OrderItems
- Calls `cart.clear()` on success

### With Store App
- Imports `Product` model
- Decrements stock on order creation

### With Settings
- Pathao credentials from environment
- Telegram credentials from environment
