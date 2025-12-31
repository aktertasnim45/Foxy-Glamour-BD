# Dependencies

> Complete list of all project dependencies with versions, purposes, and alternatives.

## Python Dependencies (requirements.txt)

| Package | Version | Purpose | Alternatives |
|---------|---------|---------|--------------|
| **Django** | ≥5.2.8 | Core web framework | Flask, FastAPI |
| **whitenoise** | ≥6.6.0 | Static file serving with compression | django-storages (S3), Nginx |
| **python-dotenv** | ≥1.0.0 | Environment variable management | django-environ, python-decouple |
| **django-jazzmin** | ≥3.0.0 | Modern admin UI theme | django-grappelli, django-suit |
| **django-import-export** | ≥4.0.0 | CSV/Excel import/export for products | django-csvimport, manual implementation |
| **Pillow** | ≥10.0.0 | Image processing for uploads | N/A (required for ImageField) |
| **requests** | ≥2.31.0 | HTTP client for APIs (Pathao, Telegram) | httpx, aiohttp |

## Installation

```bash
pip install -r requirements.txt
```

## Dependency Details

### Django ≥5.2.8 (Core Framework)

The entire application is built on Django 5.2.8. Key Django features used:

- **ORM** - Database models and queries
- **Admin** - Product/Order management
- **Sessions** - Shopping cart storage
- **Authentication** - User login/registration
- **Templates** - HTML rendering with Jinja2-like syntax
- **Static Files** - CSS, JavaScript, images
- **Migrations** - Database schema management
- **Sitemaps** - SEO sitemap generation
- **Context Processors** - Global template data

**Breaking Changes Warning:**
- Django 5.x dropped support for Python <3.10
- Some deprecated template tags removed

---

### WhiteNoise ≥6.6.0 (Static Files)

Serves static files directly from Django without requiring a separate web server like Nginx.

**Features Used:**
- `CompressedManifestStaticFilesStorage` - Gzip compression
- Automatic cache headers
- Cache-busting with file hashes

**Configuration:**
```python
# settings.py
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

---

### python-dotenv ≥1.0.0 (Environment Variables)

Loads environment variables from `.env` file for secrets management.

**Usage:**
```python
# settings.py
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')

PATHAO_CLIENT_ID = os.getenv('PATHAO_CLIENT_ID', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
```

**Security Note:** Never commit `.env` to version control.

---

### django-jazzmin ≥3.0.0 (Admin Theme)

Modern, customizable admin interface theme replacing the default Django admin look.

**Features Used:**
- Dark theme support
- Custom topmenu links (Financial Dashboard link)
- Improved UI/UX for staff users

**Configuration:**
```python
# settings.py
INSTALLED_APPS = [
    'jazzmin',  # Must come before 'django.contrib.admin'
    'django.contrib.admin',
    ...
]

JAZZMIN_SETTINGS = {
    "site_title": "Foxy Glamour Admin",
    "site_header": "Foxy Glamour",
    "theme": "darkly",
}
```

---

### django-import-export ≥4.0.0 (Data Import/Export)

Adds CSV/Excel import/export functionality to the Django admin.

**Usage:**
- Import products from spreadsheets
- Export product catalog
- Bulk update product data

**Implementation:**
```python
# store/admin.py
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price', 'stock')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
```

---

### Pillow ≥10.0.0 (Image Processing)

Required for Django's `ImageField` to work. Handles:

- Image upload validation
- Thumbnail generation (if implemented)
- Image format detection

**Note:** This is a required dependency for any Django app with image uploads.

---

### requests ≥2.31.0 (HTTP Client)

Used for external API integrations:

1. **Pathao Courier API** (`orders/pathao.py`)
   - Authentication/token refresh
   - City/Zone/Area fetching
   - Parcel creation
   - Order tracking

2. **Telegram Bot API** (`orders/telegram.py`)
   - Sending order notifications

**Example Usage:**
```python
# pathao.py
response = requests.post(url, json=payload, headers=headers)
response.raise_for_status()
return response.json()
```

---

## Django Built-in Dependencies

These come with Django and don't need separate installation:

| Module | Purpose |
|--------|---------|
| `django.contrib.admin` | Admin interface |
| `django.contrib.auth` | User authentication |
| `django.contrib.contenttypes` | Content type framework |
| `django.contrib.sessions` | Session management |
| `django.contrib.messages` | Flash messages |
| `django.contrib.staticfiles` | Static file handling |
| `django.contrib.sitemaps` | SEO sitemaps |

---

## Frontend Dependencies (CDN/Direct)

These are loaded via CDN or inline in templates:

| Resource | Source | Purpose |
|----------|--------|---------|
| **Google Fonts** | fonts.googleapis.com | Montserrat font family |
| **CSS Variables** | Inline | Dynamic theming |

---

## Development Dependencies (Optional)

Not in `requirements.txt` but recommended for development:

| Package | Purpose |
|---------|---------|
| `django-debug-toolbar` | Request/SQL debugging |
| `pytest-django` | Testing framework |
| `black` | Code formatting |
| `flake8` | Linting |

---

## System Requirements

| Requirement | Version |
|-------------|---------|
| Python | ≥3.10 (Django 5.x requirement) |
| pip | Latest |
| SQLite | 3.x (bundled with Python) |

---

## Upgrade Considerations

### Upgrading Django

```bash
pip install --upgrade Django
python manage.py migrate
python manage.py collectstatic
```

**Check for:**
- Deprecated features
- Changed URL patterns
- Template syntax changes

### Upgrading Other Packages

```bash
pip install --upgrade -r requirements.txt
```

**Test after upgrading:**
- Admin interface (Jazzmin compatibility)
- Import/Export functionality
- API integrations (requests)
- Image uploads (Pillow)
