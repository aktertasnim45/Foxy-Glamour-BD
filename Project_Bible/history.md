# Project History

> Complete development history and changelog derived from Journal.md and commit history.

## Version Timeline

| Date | Version | Milestone |
|------|---------|-----------|
| 2025-12-01 | 0.1.0 | Initial codebase analysis |
| 2025-12-02 | 0.2.0 | Shopping cart implementation |
| 2025-12-XX | 0.3.0 | Orders & checkout |
| 2025-12-XX | 0.4.0 | User authentication |
| 2025-12-XX | 0.5.0 | Local payment methods |
| 2025-12-XX | 0.6.0 | UI overhaul (Bulgari-inspired) |
| 2025-12-XX | 0.7.0 | Rebranding to Foxy Glamour |
| 2025-12-XX | 0.8.0 | Admin hero section |
| 2025-12-20 | 0.9.0 | Product zoom & checkout enhancements |
| 2025-12-24 | 0.10.0 | Performance optimizations |
| 2025-12-27 | 0.11.0 | Variation stock implementation |
| 2025-12-31 | 1.0.0 | Financial dashboard |

---

## Detailed Changelog

### Phase 1: Core Setup & Product Catalog [COMPLETED]
- Project initialized as `jewelry_site`
- Store app configured
- Product & Category models created
- Basic views (list & detail)
- Basic templates & static files
- Media settings configured

### Phase 2: Shopping Cart [COMPLETED]
**Entry 1 (2025-12-01):**
- Reviewed existing codebase
- Found: Catalog functional, "Add to Cart" button non-functional
- Decision: Implement session-based cart via new `cart` app

**Entry 2 (2025-12-02):**
- Created Blueprint.md and Journal.md
- Initialized `cart` app
- Updated settings.py with `CART_SESSION_ID`
- Created `cart/cart.py` for session handling

**Entry 3:**
- Created `cart/forms.py` - CartAddProductForm
- Created `cart/views.py` - cart_add, cart_remove, cart_detail
- Created `cart/urls.py` - URL patterns

**Entry 4:**
- Connected cart URLs to main router
- Created `cart/templates/cart/detail.html`

**Entry 5:**
- Updated `store/views.py` - injected CartAddProductForm into product detail
- Updated product detail template with add-to-cart form

**Entry 6:**
- Created `cart/context_processors.py` for global cart access
- Updated settings.py with context processor
- Updated base.html with dynamic cart count in navbar

### Phase 3: Checkout & Orders [COMPLETED]
**Entry 7:**
- Initialized `orders` app
- Created Order models

**Entry 8:**
- Created Order admin configuration
- Created OrderCreateForm
- Created checkout views and URLs

**Entry 9:**
- Created checkout template
- Created order success template
- Validated full purchase flow

### Phase 4: User Authentication [COMPLETED]
**Entry 10:**
- Initialized `accounts` app

**Entry 11:**
- Created login.html and register.html templates
- Updated navbar for dynamic user state (Login vs Logout)

**Entry 12:**
- Linked orders to users (ForeignKey)
- Created user dashboard with order history

### Phase 5: Refinements & Enhancements [ONGOING]

#### Order Success Page Fix
- **Issue:** NoReverseMatch in `orders/created.html`
- **Fix:** Updated 'Continue Shopping' link to use namespaced URL `{% url 'store:product_list' %}`
- **Result:** Order flow functional from Add to Cart → Checkout → Success

#### Local Payment Methods
- Added `payment_method` field (COD, bKash, Nagad)
- Added `transaction_id` field
- Updated OrderCreateForm with Radio Select widgets
- Added JavaScript to toggle Transaction ID fields

#### Image Display Optimization (Entry 13)
- Changed `.product-card img` from `contain` to `cover`
- Fixed excessive whitespace in product cards
- Detail view kept as `contain` for full product visibility

#### CSS Conflict Resolution (Entry 15)
- **Issue:** Duplicate CSS file in `store/static/css/` overriding main stylesheet
- **Resolution:** Deleted conflicting file
- **Result:** Images display correctly

#### Manual Payment Frontend (Entry 17)
- Updated checkout template with JavaScript toggles
- Added bKash/Nagad payment instructions

#### Major UI Overhaul (Entry 18)
- Rewrote `static/css/style.css` with premium design system
- Outfit font, deep brown/gold palette
- Added utility classes
- Refactored product_list.html - removed inline styles
- Fixed template syntax error in checkout

#### Bulgari-Inspired Redesign (Entry 19)
- Implemented "Luxe Gems" design system
- Updated header structure:
  - Top dark promo bar
  - Split utility navigation
  - Centered minimal logo
  - Clean navigation row
- Switched font to **Montserrat** (uppercase, spaced)
- Primary background: white, text: black
- Removed shadows and rounded corners
- Cache-busted CSS

#### Animated Fox Background (Entry 20)
- Generated hero background image (`hero_bg.png`)
- Implemented Hero Section with Ken Burns animation
- Optimized hero text overlay

#### Rebranding to Foxy Glamour (Entry 21)
- Updated site name from "Luxe Gems" to "Foxy Glamour"
- Updated header, hero section, page titles
- Implemented Mega Menu:
  - Added `parent` field to Category model
  - Created categories context processor
  - Recursive dropdown menu in base.html
- Created Contact Us page (`/contact/`)

#### Contact Information Update (Entry 22)
- Updated social media links:
  - Instagram: `https://www.instagram.com/foxyglamourbd2/`
  - Facebook: `https://www.facebook.com/profile.php?id=61583188543696`

#### SVG Logo Integration (Entry 23)
- Integrated user-provided `Logo.svg`
- Replaced text logo in header
- Created white version for hero section

#### Server Restart (Entry 24)
- Copied Logo.svg to static directory
- Restarted development server

### Recent Development (December 2025)

#### Button Color Customization (2025-12-19 - 2025-12-20)
- Added button color fields to Theme model
- Updated admin with button color fieldsets
- Created theme_tags template tag
- CSS uses CSS variables for button colors

#### Product Zoom Mechanism (2025-12-20)
- Implemented world-class image zoom on product detail page
- Desktop and mobile zoom variations

#### Checkout Enhancements (2025-12-20)
- Updated bKash/Nagad instructions with merchant number (01671403438)
- Enforced 11-digit phone number validation
- Made required fields: First name, Phone, Address, Postal code, City
- Made optional fields: Last name, Email
- Conditional validation for payment details

#### Discount Label Styling (2025-12-22)
- Changed discount label colors to lavender theme

#### Admin Hero Section (2025-12-20 - 2025-12-21)
- Created HeroSection model
- Admin interface with preview functionality
- Separate mobile/desktop backgrounds
- Ken Burns animation toggle

#### Performance Optimization (2025-12-24)
- Configured WhiteNoise for compression
- Implemented lazy loading for images
- Added `fetchpriority="high"` for logo
- Responsive video loading

#### Variation Stock (2025-12-27)
- Created ProductVariant model
- Size + Color combinations with individual stock
- Deployed to production server

#### Financial Dashboard (2025-12-31)
- Added `cost_price` field to Product model
- Added `cost_price` snapshot to OrderItem
- Created admin dashboard at `/admin-tools/dashboard/`
- Displays: Total Revenue, COGS, Net Profit
- Recent orders and top customers

---

## Architecture Evolution

```
v0.1 (Initial)
└── Basic catalog (Product, Category)

v0.2 (Cart)
├── Session-based cart
└── Cart context processor

v0.3 (Orders)
├── Order model
├── OrderItem model
└── Checkout flow

v0.4 (Auth)
├── User accounts
└── Order history

v0.5+ (Enhancements)
├── Payment methods
├── Theme system
├── Hero section
├── Pathao integration
├── Telegram notifications
├── Visitor tracking
├── Product variants
└── Financial dashboard
```

---

## Breaking Changes History

| Version | Change | Impact |
|---------|--------|--------|
| 0.7.0 | Renamed to Foxy Glamour | Site name changed everywhere |
| 0.11.0 | Added ProductVariant | Stock management changed |
| 1.0.0 | Added cost_price to OrderItem | Historical orders lack cost data |

---

## Migration History

Key migrations:
- `store/migrations/0001_initial.py` - Initial models
- `orders/migrations/0001_initial.py` - Order models
- `store/migrations/XXXX_herosection.py` - Hero section
- `store/migrations/XXXX_productvariant.py` - Variants
- `orders/migrations/0014_orderitem_cost_price.py` - Cost tracking
