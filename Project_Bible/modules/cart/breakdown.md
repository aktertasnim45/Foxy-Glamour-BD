# Cart Module

> Session-based shopping cart implementation.

## Overview

The `cart` app provides shopping cart functionality using Django sessions. It supports:
- Products with and without variants
- Size and color options
- Quantity management
- Session persistence

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `cart.py` | Cart class with session management | 166 |
| `views.py` | Add, remove, detail views | ~80 |
| `forms.py` | CartAddProductForm | ~30 |
| `context_processors.py` | Global cart context | 3 |
| `urls.py` | URL patterns | ~10 |
| `models.py` | Empty (session-based) | - |

---

## Cart Class (`cart.py`)

### Initialization

```python
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
```

**Session Key:** Defined in `settings.CART_SESSION_ID = 'cart'`

---

### Adding Items

```python
def add(self, product, quantity=1, override_quantity=False, size=None, color=None):
    # Build unique key: {id}_{size}_{color}
    parts = [str(product.id)]
    if size:
        parts.append(str(size))
    if color:
        parts.append(str(color))
    cart_item_key = "_".join(parts)

    if cart_item_key not in self.cart:
        self.cart[cart_item_key] = {
            'quantity': 0, 
            'price': str(product.price),
            'product_id': str(product.id),
            'size': size,
            'color': color
        }
    
    if override_quantity:
        self.cart[cart_item_key]['quantity'] = quantity
    else:
        self.cart[cart_item_key]['quantity'] += quantity
    
    self.save()
```

**Key Format Examples:**
- Product without variants: `"5"`
- Product with size: `"5_7"`
- Product with size and color: `"5_7_gold"`

---

### Removing Items

```python
def remove(self, product, size=None, color=None):
    # Build same key format
    cart_item_key = "_".join(parts)
    
    if cart_item_key in self.cart:
        del self.cart[cart_item_key]
        self.save()
```

---

### Iteration

```python
def __iter__(self):
    # Collect product IDs
    product_ids = set(item.get('product_id') for item in self.cart.values())
    
    # Fetch Size and Color objects for name resolution
    size_map = {s.code: s.name for s in Size.objects.filter(code__in=size_codes)}
    color_map = {c.code: c.name for c in Color.objects.filter(code__in=color_codes)}
    
    # Fetch products
    products = Product.objects.filter(id__in=product_ids)
    product_dict = {str(p.id): p for p in products}

    for key, item in self.cart.copy().items():
        item = item.copy()
        if product_dict.get(item.get('product_id')):
            item['product'] = product_dict[item['product_id']]
            item['net_price'] = Decimal(item['price'])
            item['total_price'] = item['net_price'] * item['quantity']
            item['size_name'] = size_map.get(item.get('size'), item.get('size'))
            item['color_name'] = color_map.get(item.get('color'), item.get('color'))
            yield item
```

**Yielded Item Structure:**
```python
{
    'quantity': 2,
    'price': '1500.00',
    'product_id': '5',
    'size': '7',
    'color': 'gold',
    'product': <Product object>,
    'net_price': Decimal('1500.00'),
    'total_price': Decimal('3000.00'),
    'size_name': 'US 7',
    'color_name': 'Gold'
}
```

---

### Other Methods

```python
def __len__(self):
    """Count all items in the cart."""
    return sum(item['quantity'] for item in self.cart.values())

def get_total_price(self):
    return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

def clear(self):
    """Remove cart from session."""
    del self.session[settings.CART_SESSION_ID]
    self.save()

def save(self):
    """Mark session as modified."""
    self.session.modified = True
```

---

## Views

### cart_add

**URL:** `POST /cart/add/<product_id>/`

```python
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                product=product,
                quantity=cd['quantity'],
                override_quantity=cd['update'],
                size=cd.get('size'),
                color=cd.get('color')
            )
    
    return redirect('cart:cart_detail')
```

---

### cart_remove

**URL:** `POST /cart/remove/<product_id>/`

```python
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    size = request.POST.get('size')
    color = request.POST.get('color')
    
    cart.remove(product, size=size, color=color)
    return redirect('cart:cart_detail')
```

---

### cart_detail

**URL:** `GET /cart/`

```python
def cart_detail(request):
    cart = Cart(request)
    # Update forms for quantity changes
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'], 'update': True}
        )
    return render(request, 'cart/detail.html', {'cart': cart})
```

---

## Forms

### CartAddProductForm

```python
class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    size = forms.CharField(required=False)
    color = forms.CharField(required=False)
```

**Usage in Templates:**
```django
<form method="post" action="{% url 'cart:cart_add' product.id %}">
    {% csrf_token %}
    <select name="size">
        {% for size in product.sizes.all %}
        <option value="{{ size.code }}">{{ size.name }}</option>
        {% endfor %}
    </select>
    <input type="number" name="quantity" value="1" min="1">
    <button type="submit">Add to Cart</button>
</form>
```

---

## Context Processor

### cart

Provides cart object to all templates.

```python
# context_processors.py
from .cart import Cart

def cart(request):
    return {'cart': Cart(request)}
```

**Usage in Templates:**
```django
<!-- In base.html navbar -->
<a href="{% url 'cart:cart_detail' %}">Bag ({{ cart|length }})</a>
```

---

## URL Patterns

```python
# urls.py
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
]
```

---

## Session Data Structure

```json
{
    "cart": {
        "1": {
            "quantity": 1,
            "price": "800.00",
            "product_id": "1",
            "size": null,
            "color": null
        },
        "5_7": {
            "quantity": 2,
            "price": "1500.00",
            "product_id": "5",
            "size": "7",
            "color": null
        },
        "5_7_gold": {
            "quantity": 1,
            "price": "1500.00",
            "product_id": "5",
            "size": "7",
            "color": "gold"
        }
    }
}
```

---

## Integration Points

### With Store App
- Imports `Product`, `Size`, `Color` models
- `CartAddProductForm` injected into product detail view

### With Orders App
- `Cart(request)` instantiated in checkout view
- Items iterated to create `OrderItem` objects
- `cart.clear()` called after successful order

---

## Edge Cases Handled

1. **Legacy Cart Items:** Old format (just product_id as key) supported
2. **Missing Products:** Silently skipped in iteration
3. **Size Resolution:** "Adjustable" handled specially
4. **Session Persistence:** `session.modified = True` ensures save
