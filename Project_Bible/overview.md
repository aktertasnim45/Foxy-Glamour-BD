# Foxy Glamour BD - Project Overview

> **Version:** 1.0.0  
> **Last Updated:** 2025-12-31  
> **Status:** Production-Ready

## Executive Summary

**Foxy Glamour BD** is a premium Django-based e-commerce platform designed for selling jewelry in Bangladesh. The platform features a modern, luxury-inspired design with full shopping cart functionality, multiple payment options (Cash on Delivery, bKash, Nagad), courier integration with Pathao, and real-time order notifications via Telegram.

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend Framework** | Django | ≥5.2.8 |
| **Database** | SQLite | (Development) |
| **Static Files** | WhiteNoise | ≥6.6.0 |
| **Admin UI** | Django Jazzmin | ≥3.0.0 |
| **Import/Export** | django-import-export | ≥4.0.0 |
| **Image Processing** | Pillow | ≥10.0.0 |
| **HTTP Client** | Requests | ≥2.31.0 |
| **Environment** | python-dotenv | ≥1.0.0 |
| **Frontend** | Vanilla CSS + Google Fonts (Montserrat) | - |

## Key Features

### 🛒 E-Commerce Core
- Product catalog with categories and subcategories (parent-child)
- Product variants (Size + Color combinations with individual stock)
- Multiple product images gallery
- Session-based shopping cart
- Discount system (percentage or fixed amount)
- Stock management with auto-decrement on order

### 💰 Payment & Checkout
- **Cash on Delivery (COD)**
- **bKash** mobile payment
- **Nagad** mobile payment
- Shipping zones (Inside Dhaka, Intercity Dhaka, Outside Dhaka)
- Order confirmation with transaction ID tracking

### 🚚 Logistics Integration
- **Pathao Courier API** integration for parcel creation
- City/Zone/Area location hierarchy
- Automatic COD amount calculation
- Order tracking via consignment ID

### 📱 Notifications
- **Telegram Bot** notifications for new orders
- Real-time order alerts to admin

### 🎨 Theming & Customization
- Admin-manageable **Theme System** (colors, buttons)
- **Hero Section** with image/video backgrounds (desktop + mobile)
- Ken Burns animation effects
- Custom logo support (SVG)

### 📊 Analytics & Admin
- **Financial Dashboard** with revenue, COGS, profit tracking
- **Visitor Tracking** middleware (IP, UTM parameters, referrer)
- Customer activity monitoring
- Traffic source analysis

### 🔐 User Management
- User registration and authentication
- Order history dashboard
- Wishlist functionality

### 🔍 SEO & Performance
- SEO-optimized product pages (meta tags, Open Graph, Twitter Cards)
- XML Sitemap generation
- robots.txt
- Static file compression & caching (WhiteNoise)

## Architecture Overview

```
                    ┌─────────────────────────────────────────┐
                    │           Django Application            │
                    └─────────────────────────────────────────┘
                                        │
        ┌───────────────┬───────────────┼───────────────┬───────────────┐
        │               │               │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │  store  │    │  cart   │    │ orders  │    │accounts │    │settings │
   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
   Products       Session Cart   Order CRUD     User Auth      Config
   Categories     Add/Remove     Checkout       Login/Logout   Middleware
   Themes         Quantity       Payment        Dashboard      
   Hero Section   Price Calc     Pathao API     Wishlist       
   Visitors                      Telegram                      
```

## Directory Structure

```
Foxy-Glamour-BD/
├── jewelry_site/          # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI entry point
├── store/                 # Main store application
│   ├── models.py          # Product, Category, Theme, Hero, etc.
│   ├── views.py           # Product listing, detail, search
│   ├── admin.py           # Admin customizations
│   ├── dashboard_views.py # Financial dashboard
│   ├── middleware.py      # Visitor tracking
│   └── templates/store/   # Store templates
├── cart/                  # Shopping cart application
│   ├── cart.py            # Cart class (session-based)
│   ├── views.py           # Add, remove, update cart
│   └── templates/cart/    # Cart templates
├── orders/                # Order management
│   ├── models.py          # Order, OrderItem, Pathao models
│   ├── views.py           # Checkout flow
│   ├── pathao.py          # Pathao API client
│   ├── telegram.py        # Telegram notifications
│   └── templates/orders/  # Order templates
├── accounts/              # User authentication
│   ├── views.py           # Login, register, dashboard
│   └── templates/accounts/# Auth templates
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   └── img/               # Images (logo, hero)
├── media/                 # User uploads
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── manage.py              # Django management script
```

## Environment Variables (.env)

| Variable | Description |
|----------|-------------|
| `PATHAO_CLIENT_ID` | Pathao API client ID |
| `PATHAO_CLIENT_SECRET` | Pathao API client secret |
| `PATHAO_CLIENT_EMAIL` | Pathao account email |
| `PATHAO_CLIENT_PASSWORD` | Pathao account password |
| `PATHAO_STORE_ID` | Pathao registered store ID |
| `PATHAO_SENDER_PHONE` | Sender phone for parcels |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for notifications |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/aktertasnim45/Foxy-Glamour-BD.git
cd Foxy-Glamour-BD

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Edit .env with your credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver
```

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage / Product listing |
| `/<category-slug>/` | Category filtered products |
| `/<id>/<slug>/` | Product detail page |
| `/search/` | Search page |
| `/cart/` | Shopping cart |
| `/orders/create/` | Checkout page |
| `/accounts/login/` | Login page |
| `/accounts/register/` | Registration page |
| `/accounts/dashboard/` | User dashboard |
| `/wishlist/` | User wishlist |
| `/contact/` | Contact page |
| `/about/` | About page |
| `/admin/` | Django admin |
| `/admin-tools/dashboard/` | Financial dashboard |

## Business Context

- **Target Market:** Bangladesh (Bengali Taka - ৳)
- **Shipping Zones:**
  - Inside Dhaka: ৳80
  - Intercity Dhaka: ৳120
  - Outside Dhaka: ৳150
- **Payment Methods:** COD (default), bKash, Nagad
- **Merchant Mobile:** 01671403438 (for bKash/Nagad payments)
