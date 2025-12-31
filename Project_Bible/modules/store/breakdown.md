# Store Module

> Core application handling products, categories, themes, and homepage functionality.

## Overview

The `store` app is the heart of the Foxy Glamour BD e-commerce platform. It manages:
- Products and product variants
- Categories with hierarchical structure
- Site theming and hero section
- Visitor analytics
- Financial dashboard

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `models.py` | 10 models: Product, Category, Theme, HeroSection, etc. | 374 |
| `views.py` | Product list, detail, search, wishlist views | 182 |
| `admin.py` | Admin configuration with import/export | 253 |
| `dashboard_views.py` | Financial dashboard for staff | 57 |
| `context_processors.py` | Global template contexts | 16 |
| `middleware.py` | Visitor tracking | 53 |
| `sitemaps.py` | SEO sitemaps | ~50 |
| `urls.py` | URL routing | 20 |

---

## Models

### Category
Hierarchical product categories with parent-child relationships.

```python
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', related_name='children', 
                               on_delete=models.CASCADE, null=True, blank=True)
```

**Key Methods:**
- `get_absolute_url()` → `/category-slug/`

---

### Size & Color
Product attribute options.

```python
class Size(models.Model):
    name = models.CharField(max_length=20)  # "US 7", "Small"
    code = models.SlugField(max_length=20, unique=True)  # "7", "s"

class Color(models.Model):
    name = models.CharField(max_length=20)  # "Gold", "Silver"
    code = models.SlugField(max_length=20, unique=True)  # "gold", "silver"
```

---

### Product
Main product model with 20+ fields.

**Core Fields:**
- `name`, `slug`, `category`, `image`, `description`
- `price`, `cost_price`
- `metal` (choices: Gold, Silver, Platinum, Rose Gold, Brass)
- `gemstone`
- `available`, `stock`
- `is_adjustable`
- `sizes` (M2M), `colors` (M2M)

**Discount Fields:**
- `discount_percentage` (0-100)
- `discount_amount` (fixed TK)

**List Image Customization:**
- `list_image_fit`: "cover" or "contain"
- `list_image_position`: center, top, bottom, left, right

**SEO Fields:**
- `meta_title`, `meta_description`, `meta_keywords`

**Key Properties:**
```python
@property
def has_discount(self):
    return bool(self.discount_percentage or self.discount_amount)

@property
def discounted_price(self):
    if self.discount_percentage:
        return round(self.price - (self.price * self.discount_percentage / 100), 2)
    elif self.discount_amount:
        return max(self.price - self.discount_amount, 0)
    return self.price
```

**Custom Save:**
Auto-calculates `discount_percentage` when `discount_amount` changes.

---

### ProductImage
Multiple gallery images per product.

```python
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/%Y/%m/%d')
```

---

### ProductVariant
Stock management for Size + Color combinations.

```python
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size', 'color')
```

---

### Theme
Site-wide color theming.

**Fields:**
- General: `primary_color`, `text_color`, `bg_color`, `accent_color`, `promo_bg`
- Primary Button: `button_bg_color`, `button_text_color`, `button_hover_bg_color`
- Buy Now Button: `buy_now_bg_color`, `buy_now_text_color`, `buy_now_hover_bg_color`, `buy_now_hover_text_color`

**Singleton Pattern:** Only one theme can be `is_active=True` at a time.

---

### HeroSection
Homepage hero configuration with image/video backgrounds.

**Background Options:**
- Desktop: `background_type`, `background_image`, `background_video`
- Mobile: `mobile_background_type`, `mobile_background_image`, `mobile_background_video`

**Content:**
- `logo`, `headline`, `tagline`
- `show_logo`, `show_headline`, `show_tagline`
- `enable_ken_burns` (animation)

---

### Wishlist
User wishlist with unique user+product constraint.

---

### Visitor
Analytics tracking for page visits.

**Fields:**
- `ip_address`, `user_agent`, `path`, `referer`
- `utm_source`, `utm_medium`, `utm_campaign`
- `created` (timestamp)

---

## Views

### product_list
Homepage and category pages.

**URL:** `/` or `/<category_slug>/`

**Features:**
- Category filtering
- Search filtering (name, description)
- Price filtering (min/max)
- Sorting (newest, price_asc, price_desc)

**Context:**
- `products`, `category`, `categories`
- `sort_by`, URL helpers

---

### product_detail
Product detail page.

**URL:** `/<id>/<slug>/`

**Features:**
- Product information
- Related products (same category)
- Variants serialized to JSON for frontend

**Context:**
- `product`, `cart_product_form`
- `related_products`, `variants_json`

---

### search
Advanced search page.

**URL:** `/search/?q=...&category=...&min_price=...&max_price=...&metal=...&sort=...`

**Features:**
- Text search (name, description, gemstone, metal)
- Category filter
- Price range filter
- Metal filter
- Sort options

---

### Wishlist Views
- `wishlist_list` - View user's wishlist
- `wishlist_add` - Add product to wishlist
- `wishlist_remove` - Remove from wishlist

All require `@login_required`.

---

### contact & about
Static pages.

---

## Admin Configuration

### ProductAdmin
- Import/Export support via `ProductResource`
- Inlines: `ProductImageInline`, `ProductVariantInline`
- List display: name, price, stock, available, sizes, colors
- List editable: price, stock, available
- Fieldsets: Basic, Pricing, Inventory, Details, SEO

### CategoryAdmin
- Import/Export support
- Prepopulated slug

### ThemeAdmin
- Fieldsets for general colors and button colors
- List editable for quick color changes

### HeroSectionAdmin
- Preview thumbnails in list view
- Large preview in change form
- Custom action: "Set selected hero as active"

---

## Context Processors

### categories
Provides root categories to all templates.
```python
def categories(request):
    return {'categories': Category.objects.filter(parent=None)}
```

### active_theme
Provides active theme to all templates.
```python
def active_theme(request):
    return {'active_theme': Theme.objects.filter(is_active=True).first()}
```

### active_hero
Provides active hero section configuration.
```python
def active_hero(request):
    return {'active_hero': HeroSection.objects.filter(is_active=True).first()}
```

---

## Middleware

### VisitorTrackingMiddleware
Tracks every page visit (excluding admin, static, media).

**Data Captured:**
- IP address (X-Forwarded-For or REMOTE_ADDR)
- User agent
- Page path
- Referrer URL
- UTM parameters

---

## Dashboard Views

### admin_dashboard
Staff-only financial dashboard.

**URL:** `/admin-tools/dashboard/`

**Metrics:**
- Total orders
- Total revenue
- Total COGS (cost of goods sold)
- Net profit
- Recent orders (last 10)
- Top customers
- Visitors today
- Top traffic sources

---

## URL Patterns

```python
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('admin-tools/dashboard/', dashboard_views.admin_dashboard, name='admin_dashboard'),
]
```

**App namespace:** `store`
