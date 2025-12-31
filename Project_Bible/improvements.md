# Improvements & Roadmap

> Suggestions for optimizations, refactors, new features, and technical debt remediation.

## Priority Matrix

| Priority | Impact | Effort | Category |
|----------|--------|--------|----------|
| 🔴 Critical | High impact, should do now | | |
| 🟠 High | Important for scale/UX | | |
| 🟡 Medium | Nice to have | | |
| 🟢 Low | Future consideration | | |

---

## 1. Performance Optimizations

### 🔴 Database Query Optimization
**Current Issue:** N+1 queries in cart iteration and order display.

**Recommendation:**
```python
# cart.py - Use select_related for products
products = Product.objects.filter(id__in=product_ids).select_related('category')

# orders/views.py - Prefetch related items
Order.objects.select_related('user').prefetch_related('items__product')
```

**Impact:** 50-80% reduction in database queries.

---

### 🟠 Image Optimization
**Current:** Full-resolution images served everywhere.

**Recommendations:**
1. Implement django-imagekit for automatic thumbnails
2. WebP format with fallbacks
3. Lazy loading (partially implemented)
4. Responsive `srcset` attributes

```python
# Example with django-imagekit
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Product(models.Model):
    image = models.ImageField(...)
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(300, 300)],
        format='WEBP',
        options={'quality': 80}
    )
```

---

### 🟡 Caching Strategy
**Current:** No explicit caching beyond WhiteNoise static files.

**Recommendations:**
1. Cache category tree (context processor)
2. Cache active theme (single DB query per request currently)
3. Cache product counts per category
4. Redis for session storage (production)

```python
# context_processors.py
from django.core.cache import cache

def categories(request):
    cats = cache.get('root_categories')
    if not cats:
        cats = list(Category.objects.filter(parent=None))
        cache.set('root_categories', cats, 3600)  # 1 hour
    return {'categories': cats}
```

---

## 2. Code Quality Improvements

### 🔴 Stock Validation on Checkout
**Current Issue:** Stock not validated before order creation, could go negative.

**Fix:**
```python
# orders/views.py
for item in cart:
    product = item['product']
    if product.stock < item['quantity']:
        messages.error(request, f"Not enough stock for {product.name}")
        return redirect('cart:cart_detail')
```

---

### 🟠 Form Validation Improvements
**Current Issue:** bKash/Nagad fields only validated on frontend.

**Fix:**
```python
# orders/forms.py
def clean(self):
    cleaned_data = super().clean()
    payment = cleaned_data.get('payment_method')
    
    if payment in ['bkash', 'nagad']:
        if not cleaned_data.get('bkash_number'):
            self.add_error('bkash_number', 'Required for mobile payment')
        if not cleaned_data.get('transaction_id'):
            self.add_error('transaction_id', 'Required for mobile payment')
    
    return cleaned_data
```

---

### 🟡 Type Hints
**Current:** No type hints in Python code.

**Recommendation:** Add type hints for better IDE support and documentation.

```python
# Before
def add(self, product, quantity=1, override_quantity=False, size=None, color=None):

# After
from store.models import Product

def add(
    self, 
    product: Product, 
    quantity: int = 1, 
    override_quantity: bool = False, 
    size: str | None = None, 
    color: str | None = None
) -> None:
```

---

### 🟡 Split Large Files
**Current:** `store/models.py` is 374 lines with 10+ models.

**Recommendation:** Split into:
- `store/models/product.py`
- `store/models/theme.py`
- `store/models/hero.py`
- `store/models/visitor.py`
- `store/models/__init__.py` (imports all)

---

## 3. Feature Enhancements

### 🟠 Cart Persistence for Logged-in Users
**Current:** Cart stored in session, lost on logout/new browser.

**Recommendation:** Database-backed cart for authenticated users.

```python
# New model
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, null=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
```

---

### 🟠 Email Notifications
**Current:** Only Telegram notifications.

**Recommendation:** Email confirmation to customers.

```python
from django.core.mail import send_mail

def send_order_confirmation(order):
    send_mail(
        subject=f'Order #{order.id} Confirmed',
        message=f'Thank you for your order...',
        from_email='orders@foxyglamour.com',
        recipient_list=[order.email],
    )
```

---

### 🟡 Order Tracking Page
**Current:** Users can only view orders in dashboard.

**Recommendation:** Public tracking page with order ID + phone verification.

URL: `/track/?order_id=123&phone=01712345678`

---

### 🟡 Product Reviews
**Current:** No review/rating system.

**Recommendation:**
```python
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1,1),(2,2),(3,3),(4,4),(5,5)])
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
```

---

### 🟡 Inventory Alerts
**Current:** No notification when stock runs low.

**Recommendation:**
```python
# In Product.save() or signals
if self.stock <= 5:
    send_low_stock_alert(self)
```

---

### 🟢 Coupon/Promo Codes
**Future Enhancement:**
```python
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(choices=[('percent','%'),('fixed','TK')])
    discount_value = models.DecimalField(...)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(null=True)
    times_used = models.IntegerField(default=0)
```

---

### 🟢 Wishlist Sharing
**Future:** Allow users to share wishlists via unique link.

---

## 4. Security Improvements

### 🔴 Secret Key Management
**Current:** Secret key hardcoded in settings.py.

**Fix:** Move to environment variable:
```python
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-for-dev-only')
```

---

### 🟠 DEBUG Mode
**Current:** `DEBUG = True` hardcoded.

**Fix:**
```python
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
```

---

### 🟠 ALLOWED_HOSTS
**Current:** `ALLOWED_HOSTS = ['*']` (accepts all).

**Fix:** Restrict to actual domains:
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
```

---

### 🟡 CSRF & Security Headers
**Recommendations:**
```python
# settings.py
CSRF_COOKIE_SECURE = True  # Production
SESSION_COOKIE_SECURE = True  # Production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 5. DevOps & Infrastructure

### 🟠 Database Migration to PostgreSQL
**Current:** SQLite (development-grade).

**Recommendation:** PostgreSQL for production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

---

### 🟠 Automated Testing
**Current:** No tests written.

**Recommendation:** pytest-django test suite:
- Unit tests for models
- Integration tests for views
- Cart flow tests
- Order creation tests

---

### 🟡 CI/CD Pipeline
**Recommendation:** GitHub Actions workflow:
```yaml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python manage.py test
```

---

### 🟢 Docker Containerization
**Future:** Dockerfile for consistent deployments.

---

## 6. UX Improvements

### 🟠 Loading States
**Current:** No loading indicators on AJAX actions.

**Recommendation:** Add spinners for:
- Add to cart
- Cart updates
- Checkout submission

---

### 🟠 Error Messages
**Current:** Generic error handling.

**Recommendation:** User-friendly, specific error messages.

---

### 🟡 Search Enhancements
**Current:** Basic LIKE search on name/description.

**Recommendations:**
- PostgreSQL full-text search
- Elasticsearch integration
- Autocomplete suggestions
- Search analytics

---

## Roadmap Summary

| Quarter | Focus Area |
|---------|------------|
| Q1 2026 | Security fixes, stock validation, PostgreSQL |
| Q2 2026 | Email notifications, testing suite, performance |
| Q3 2026 | Reviews, coupons, advanced search |
| Q4 2026 | Mobile app API, advanced analytics |
