# Logic Flows

> Detailed flowcharts and sequence diagrams for key business processes in Foxy Glamour BD.

## Table of Contents
1. [User Purchase Flow](#1-user-purchase-flow)
2. [Add to Cart Flow](#2-add-to-cart-flow)
3. [Checkout & Order Creation](#3-checkout--order-creation)
4. [Product Display Flow](#4-product-display-flow)
5. [Theme Application Flow](#5-theme-application-flow)
6. [Visitor Tracking Flow](#6-visitor-tracking-flow)
7. [Pathao Integration Flow](#7-pathao-integration-flow)
8. [Telegram Notification Flow](#8-telegram-notification-flow)
9. [Discount Calculation Flow](#9-discount-calculation-flow)

---

## 1. User Purchase Flow

Complete end-to-end purchase journey.

```mermaid
flowchart TD
    A[User visits homepage] --> B[Browse/Search Products]
    B --> C[View Product Detail]
    C --> D{Select Size/Color?}
    D -->|Yes| E[Select Options]
    D -->|No/Adjustable| F[Add to Cart]
    E --> F
    F --> G[Continue Shopping?]
    G -->|Yes| B
    G -->|No| H[View Cart]
    H --> I[Proceed to Checkout]
    I --> J[Fill Customer Details]
    J --> K{Payment Method?}
    K -->|COD| L[Submit Order]
    K -->|bKash/Nagad| M[Enter Transaction ID]
    M --> L
    L --> N[Order Created]
    N --> O[Telegram Notification Sent]
    N --> P[Stock Decremented]
    N --> Q[Success Page]
```

---

## 2. Add to Cart Flow

Session-based cart management.

```mermaid
sequenceDiagram
    participant U as User
    participant V as View (cart_add)
    participant F as CartAddProductForm
    participant C as Cart Class
    participant S as Session

    U->>V: POST /cart/add/{product_id}/
    V->>F: Validate form data
    F-->>V: quantity, update, size, color
    V->>C: cart.add(product, quantity, options)
    
    Note over C: Build cart key: "{id}_{size}_{color}"
    
    C->>S: Check if key exists
    
    alt Key exists
        C->>S: Update quantity
    else Key doesn't exist
        C->>S: Create new entry
    end
    
    C->>S: Mark session modified
    V-->>U: Redirect to cart or product
```

**Cart Session Structure:**
```python
# Session['cart'] example:
{
    "5_7_gold": {
        "quantity": 2,
        "price": "1500.00",
        "product_id": "5",
        "size": "7",
        "color": "gold"
    }
}
```

---

## 3. Checkout & Order Creation

Order submission and processing.

```mermaid
flowchart TD
    A[User clicks Checkout] --> B[order_create view]
    B --> C{Request Method?}
    
    C -->|GET| D[Pre-fill form if logged in]
    D --> E[Render checkout template]
    
    C -->|POST| F[Validate OrderCreateForm]
    F --> G{Valid?}
    
    G -->|No| E
    G -->|Yes| H[Create Order object]
    
    H --> I{User logged in?}
    I -->|Yes| J[Attach user to order]
    I -->|No| K[Guest order]
    J --> L[Save Order]
    K --> L
    
    L --> M[Loop through cart items]
    
    subgraph Create Order Items
        M --> N[Create OrderItem]
        N --> O[Snapshot price & cost_price]
        O --> P[Decrement product stock]
        P --> Q{More items?}
        Q -->|Yes| M
    end
    
    Q -->|No| R[Send Telegram notification]
    R --> S[Clear cart]
    S --> T[Render success page]
```

**Order Creation Code Path:**
1. `orders/views.py:order_create()` - Main view
2. `orders/forms.py:OrderCreateForm` - Form validation
3. `orders/models.py:Order` - Order model
4. `orders/models.py:OrderItem` - Line items
5. `orders/telegram.py:send_order_notification()` - Notification

---

## 4. Product Display Flow

Product listing and detail page rendering.

```mermaid
flowchart TD
    A[Request to /] --> B{Category filter?}
    
    B -->|Yes| C[Filter by category]
    B -->|No| D[All available products]
    
    C --> E{Search query?}
    D --> E
    
    E -->|Yes| F[Filter by name/description]
    E -->|No| G{Price filter?}
    
    F --> G
    
    G -->|Yes| H[Apply min/max price]
    G -->|No| I{Sort order?}
    
    H --> I
    
    I --> J[Order by sort param]
    J --> K[Render product_list.html]
    
    subgraph Template Context
        L[products queryset]
        M[active category]
        N[sort parameters]
        O[hero section data]
    end
    
    K --> P[Display Hero Section]
    P --> Q[Display Product Grid]
```

**Product Detail Flow:**
```mermaid
flowchart TD
    A[Request to /{id}/{slug}/] --> B[get_object_or_404]
    B --> C[Product available?]
    
    C -->|No| D[404 Page]
    C -->|Yes| E[Build context]
    
    E --> F[Get related products]
    F --> G[Serialize variants to JSON]
    G --> H[Initialize CartAddProductForm]
    
    H --> I[Render product_detail.html]
    
    I --> J[Display main image]
    J --> K[Display gallery images]
    K --> L[Display size/color selectors]
    L --> M[Show stock availability]
    M --> N[Display price with discount]
```

---

## 5. Theme Application Flow

Dynamic theming via context processor.

```mermaid
sequenceDiagram
    participant R as Request
    participant CP as context_processors.py
    participant TM as Theme Model
    participant T as Template
    participant TT as theme_tags.py

    R->>CP: Request made
    CP->>TM: Theme.objects.filter(is_active=True).first()
    TM-->>CP: Return active theme
    CP-->>R: Context: {'active_theme': theme}
    
    R->>T: Render base.html
    T->>TT: {% theme_styles active_theme %}
    TT-->>T: style="--primary-color: #xxx; ..."
    
    Note over T: CSS uses var(--primary-color)
```

**Theme Variables Injected:**
- `--primary-color`
- `--text-color`
- `--bg-color`
- `--accent-color`
- `--promo-bg`
- `--btn-bg`, `--btn-text`, `--btn-hover`
- `--btn-buy-bg`, `--btn-buy-text`, `--btn-buy-hover-bg`

---

## 6. Visitor Tracking Flow

Analytics middleware tracking.

```mermaid
flowchart TD
    A[Incoming Request] --> B{Path contains admin/static/media?}
    
    B -->|Yes| C[Skip tracking]
    B -->|No| D[Extract visitor data]
    
    D --> E[Get IP from X-Forwarded-For or REMOTE_ADDR]
    E --> F[Get User-Agent]
    F --> G[Get Referer]
    G --> H[Extract UTM parameters]
    
    H --> I[Create Visitor record]
    I --> J[Continue to view]
    
    C --> J
```

**Data Captured:**
- IP Address
- User Agent (browser/device)
- Page path
- Referrer URL
- UTM Source
- UTM Medium
- UTM Campaign
- Timestamp

---

## 7. Pathao Integration Flow

Courier API integration for order fulfillment.

```mermaid
sequenceDiagram
    participant A as Admin
    participant O as Order Admin
    participant PC as PathaoClient
    participant PA as Pathao API
    participant C as Cache

    A->>O: Click "Send to Pathao"
    O->>PC: create_parcel(order)
    
    PC->>C: Check for cached token
    
    alt Token cached
        C-->>PC: Return token
    else No token
        PC->>PA: POST /issue-token
        PA-->>PC: access_token
        PC->>C: Cache token (1 hour)
    end
    
    PC->>PA: POST /orders (create parcel)
    
    Note over PC,PA: Payload includes:<br/>store_id, recipient details,<br/>items, COD amount
    
    PA-->>PC: Response with consignment_id
    
    PC->>O: Update order.pathao_consignment_id
    PC->>O: Update order.sent_to_pathao = True
    
    O-->>A: Success message
```

---

## 8. Telegram Notification Flow

Order notification to admin.

```mermaid
flowchart TD
    A[Order Created] --> B[send_order_notification]
    B --> C{Telegram configured?}
    
    C -->|No| D[Log warning, skip]
    C -->|Yes| E[Build message]
    
    E --> F[Format customer details]
    F --> G[Format item list]
    G --> H[Format totals]
    
    H --> I[POST to Telegram API]
    I --> J{Success?}
    
    J -->|Yes| K[Return True]
    J -->|No| L[Log error]
    L --> M[Return False]
    
    D --> N[Continue without notification]
    K --> N
    M --> N
```

**Message Format:**
```
🛒 New Order #123

👤 Customer:
John Doe
📞 01712345678
📧 john@example.com

📍 Address:
123 Main Street
Dhaka, 1205
🚚 Inside Dhaka (80 TK)

📦 Items:
  • Gold Ring x2 = ৳3000
  • Silver Bracelet x1 = ৳1500

💰 Subtotal: ৳4500
🚚 Shipping: ৳80
💵 Total: ৳4580

💳 Payment: Cash on Delivery
⏰ 31 Dec 2025, 08:30 PM
```

---

## 9. Discount Calculation Flow

Automatic discount handling.

```mermaid
flowchart TD
    A[Product.save called] --> B{discount_amount changed?}
    
    B -->|No| C[Standard save]
    B -->|Yes| D{discount_amount > 0?}
    
    D -->|Yes| E[Calculate percentage]
    E --> F["percentage = (amount / price) × 100"]
    F --> G[Set discount_percentage]
    
    D -->|No| H[Clear discount_percentage]
    
    G --> C
    H --> C
```

**Discount Price Calculation:**
```python
@property
def discounted_price(self):
    if self.discount_percentage:
        # Percentage takes priority
        discount = self.price * (self.discount_percentage / 100)
        return round(self.price - discount, 2)
    elif self.discount_amount:
        # Fixed amount discount
        return max(self.price - self.discount_amount, 0)
    return self.price  # No discount
```

---

## Key Decision Points

### Cart Key Generation
```python
# Format: {product_id}_{size}_{color}
parts = [str(product.id)]
if size:
    parts.append(str(size))
if color:
    parts.append(str(color))
cart_item_key = "_".join(parts)
```

### Stock Management
- Stock decremented immediately on order creation
- Prevents negative stock with `max(stock - qty, 0)`
- Variant-level stock if `ProductVariant` exists

### Order Status Flow
```
Pending → Processing → Shipped → Delivered
                   ↘ Cancelled
```
