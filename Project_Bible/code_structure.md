# Code Structure

> Comprehensive breakdown of all files and directories in the Foxy Glamour BD project.

## Root Directory Tree

```
Foxy-Glamour-BD/
│
├── 📁 jewelry_site/           # Django project configuration
│   ├── __init__.py
│   ├── settings.py            # All Django settings, middleware, installed apps
│   ├── urls.py                # Root URL router (admin, accounts, cart, orders, store)
│   ├── wsgi.py                # WSGI application for deployment
│   └── asgi.py                # ASGI application for async support
│
├── 📁 store/                  # Main store application (Products, Categories, Themes)
│   ├── __init__.py
│   ├── admin.py               # Product, Category, Theme, Hero admin with import/export
│   ├── apps.py                # App configuration
│   ├── context_processors.py  # Global template contexts (categories, theme, hero)
│   ├── dashboard_views.py     # Financial dashboard view
│   ├── middleware.py          # Visitor tracking middleware
│   ├── models.py              # 10+ models: Product, Category, Theme, HeroSection, etc.
│   ├── sitemaps.py            # SEO sitemaps for products, categories
│   ├── urls.py                # Store URL patterns
│   ├── views.py               # Product list, detail, search, wishlist views
│   │
│   ├── 📁 templates/store/
│   │   ├── base.html          # Master template (header, nav, footer)
│   │   ├── product_list.html  # Homepage/category product grid
│   │   ├── product_detail.html# Product detail page with gallery
│   │   ├── search.html        # Search results page
│   │   ├── contact.html       # Contact us page
│   │   ├── about.html         # About us page
│   │   ├── wishlist.html      # User wishlist
│   │   └── dashboard.html     # Admin financial dashboard
│   │
│   ├── 📁 templatetags/
│   │   └── theme_tags.py      # Custom template tags for dynamic theming
│   │
│   └── 📁 migrations/         # Database migrations
│
├── 📁 cart/                   # Shopping cart application
│   ├── __init__.py
│   ├── admin.py               # (Empty - cart is session-based)
│   ├── apps.py                # App configuration
│   ├── cart.py                # Cart class: add, remove, iterate, total
│   ├── context_processors.py  # Global cart context
│   ├── forms.py               # CartAddProductForm
│   ├── models.py              # (Empty - session-based)
│   ├── urls.py                # Cart URL patterns
│   ├── views.py               # cart_add, cart_remove, cart_detail
│   │
│   ├── 📁 templates/cart/
│   │   └── detail.html        # Cart page template
│   │
│   └── 📁 migrations/
│
├── 📁 orders/                 # Order management application
│   ├── __init__.py
│   ├── admin.py               # Order admin with Pathao integration
│   ├── apps.py                # App configuration
│   ├── forms.py               # OrderCreateForm with validation
│   ├── models.py              # Order, OrderItem, PathaoCity/Zone/Area
│   ├── pathao.py              # Pathao Courier API client
│   ├── telegram.py            # Telegram notification service
│   ├── urls.py                # Orders URL patterns
│   ├── views.py               # order_create view
│   │
│   ├── 📁 templates/orders/order/
│   │   ├── create.html        # Checkout form
│   │   └── created.html       # Order success page
│   │
│   ├── 📁 management/commands/
│   │   └── sync_pathao_locations.py  # Command to sync Pathao locations
│   │
│   └── 📁 migrations/
│
├── 📁 accounts/               # User authentication application
│   ├── __init__.py
│   ├── admin.py               # (Uses Django's built-in User admin)
│   ├── apps.py                # App configuration
│   ├── models.py              # (Uses Django's built-in User)
│   ├── urls.py                # Auth URL patterns
│   ├── views.py               # register, login, dashboard
│   │
│   ├── 📁 templates/accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── password_change_form.html
│   │   └── password_change_done.html
│   │
│   └── 📁 migrations/
│
├── 📁 static/                 # Static assets (CSS, images)
│   ├── 📁 css/
│   │   ├── style.css          # Main stylesheet (~49KB, comprehensive design system)
│   │   ├── new_pdp_style.css  # Product detail page specific styles
│   │   └── admin_custom.css   # Admin panel customizations
│   │
│   └── 📁 img/
│       ├── logo.svg           # Site logo
│       ├── logo_white.svg     # White version of logo
│       └── hero_bg.png        # Hero section background image
│
├── 📁 staticfiles/            # Collected static files (for production)
│
├── 📁 media/                  # User-uploaded files
│   ├── 📁 products/           # Product images
│   └── 📁 hero/               # Hero section media
│
├── 📁 Pathao_integration/     # Pathao documentation/reference
│
├── 📁 venv/                   # Python virtual environment
│
├── .env                       # Environment variables (secrets)
├── .gitignore                 # Git ignore rules
├── db.sqlite3                 # SQLite database
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Blueprint.md               # Project roadmap
└── Journal.md                 # Development journal/changelog
```

## File Counts by Type

| Extension | Count | Description |
|-----------|-------|-------------|
| `.py` | ~40+ | Python source files (models, views, etc.) |
| `.html` | ~20 | Django templates |
| `.css` | 3 | Stylesheets |
| `.svg` | 2 | Logo files |
| `.png` | 1 | Hero background |
| `.md` | 2 | Documentation (Blueprint, Journal) |
| `.txt` | 1 | Requirements |
| `.toml/.env` | 1 | Environment configuration |

## Key Files Deep Dive

### `jewelry_site/settings.py`
- **INSTALLED_APPS:** jazzmin, store, cart, orders, accounts, import_export
- **MIDDLEWARE:** whitenoise, VisitorTrackingMiddleware
- **CONTEXT_PROCESSORS:** cart, categories, active_theme, active_hero
- **STATICFILES_STORAGE:** WhiteNoise with compression
- **External integrations:** Pathao API, Telegram Bot

### `store/models.py` (374 lines)
Core data models:
- `Category` - Product categories with parent-child relationships
- `Size` - Product sizes (e.g., "US 7", "Small")
- `Color` - Product colors
- `Product` - Main product model with 20+ fields
- `ProductImage` - Multiple images per product
- `ProductVariant` - Size/Color combinations with individual stock
- `Wishlist` - User wishlists
- `Theme` - Site theming (colors, buttons)
- `HeroSection` - Homepage hero configuration
- `Visitor` - Visitor tracking data

### `cart/cart.py` (166 lines)
Session-based cart implementation:
- `Cart.__init__()` - Initialize from session
- `Cart.add()` - Add product with size/color
- `Cart.remove()` - Remove specific variant
- `Cart.__iter__()` - Iterate with product details
- `Cart.get_total_price()` - Calculate total
- `Cart.clear()` - Clear cart on order completion

### `orders/pathao.py` (234 lines)
Pathao Courier API integration:
- `PathaoClient` - API client class
- Token management with caching
- City/Zone/Area location fetching
- Parcel creation for orders
- Order status tracking

### `static/css/style.css` (~49KB)
Comprehensive design system:
- CSS variables for theming
- Responsive breakpoints
- Product grid layouts
- Cart and checkout styling
- Hero section with Ken Burns animation
- Mobile navigation

## Template Hierarchy

```
base.html
├── product_list.html (Homepage, Category pages)
├── product_detail.html (PDP with gallery, add-to-cart)
├── search.html (Search results)
├── contact.html (Contact information)
├── about.html (About page)
├── wishlist.html (User wishlist)
└── dashboard.html (Admin financial dashboard)

cart/detail.html (Shopping cart - extends base.html)

orders/order/
├── create.html (Checkout form - extends base.html)
└── created.html (Order success - extends base.html)

accounts/
├── login.html (Login form)
├── register.html (Registration form)
├── dashboard.html (User order history)
├── password_change_form.html
└── password_change_done.html
```
