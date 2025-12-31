# Edge Cases & Known Issues

> Documentation of edge cases, potential issues, error handling, and testing scenarios.

## Table of Contents
1. [Cart Edge Cases](#cart-edge-cases)
2. [Order Edge Cases](#order-edge-cases)
3. [Product Edge Cases](#product-edge-cases)
4. [Payment Edge Cases](#payment-edge-cases)
5. [API Integration Edge Cases](#api-integration-edge-cases)
6. [Template/Frontend Edge Cases](#templatefrontend-edge-cases)
7. [Known Bugs & Limitations](#known-bugs--limitations)

---

## Cart Edge Cases

### 1. Legacy Cart Items
**Scenario:** Cart items added before size/color variants were implemented.

**Issue:** Old cart format uses just `product_id` as key, new format uses `{product_id}_{size}_{color}`.

**Handling:**
```python
# cart.py __iter__ method handles both formats
if '_' not in key:
    p_id = key  # Legacy key IS the product_id
```

### 2. Product Deleted While in Cart
**Scenario:** User adds product, admin deletes it, user views cart.

**Handling:** Current code skips items where product doesn't exist:
```python
if p_id and p_id in product_dict:
    # Process item
# Else: item silently ignored
```

**Improvement:** Should notify user that items were removed.

### 3. Size/Color No Longer Available
**Scenario:** User adds product with size "7", admin removes size from product.

**Current Behavior:** Cart shows size code/name from session, product may be unpurchaseable.

**Improvement:** Validate cart items on checkout against current product configuration.

### 4. Zero Quantity Items
**Scenario:** User sets quantity to 0 via update form.

**Handling:** View should remove item or treat as 1:
```python
if quantity <= 0:
    cart.remove(product, size, color)
```

### 5. Concurrent Session Updates
**Scenario:** Same session updated from multiple browser tabs.

**Risk:** Race condition could cause quantity mismatch.

**Mitigation:** Django sessions are atomic per request, but UI should refresh after add.

---

## Order Edge Cases

### 1. Stock Depleted During Checkout
**Scenario:** User adds product (stock=2), another user buys 2 units, first user checks out.

**Current Behavior:** Stock goes negative (prevented by `max(0)` safeguard).

**Code:**
```python
product.stock -= item['quantity']
if product.stock < 0:
    product.stock = 0  # Safety
```

**Improvement:** Check stock before order creation, show error if insufficient.

### 2. Payment Method Validation
**Scenario:** User selects bKash but leaves transaction ID empty.

**Current Handling:** Frontend JavaScript toggles required fields. Backend should also validate:
```python
# orders/forms.py should enforce:
if payment_method in ['bkash', 'nagad']:
    if not transaction_id or not bkash_number:
        raise ValidationError("Transaction details required")
```

### 3. Guest vs. Logged-in Orders
**Scenario:** User places order as guest, then registers with same email.

**Issue:** Orders are not automatically linked to new account.

**Behavior:** 
- Guest orders: `order.user = None`
- Logged-in: `order.user = request.user`

### 4. Empty Cart Checkout
**Scenario:** User navigates directly to `/orders/create/` with empty cart.

**Handling:** View should redirect:
```python
if len(cart) == 0:
    return redirect('cart:cart_detail')
```

### 5. Phone Number Format
**Constraint:** Bangladesh numbers must be exactly 11 digits.

**Validation:** Model enforces `max_length=11`, frontend should enforce pattern.

---

## Product Edge Cases

### 1. Discount Conflicts
**Scenario:** Both `discount_percentage` and `discount_amount` are set.

**Priority:** Percentage takes precedence:
```python
if self.discount_percentage:
    # Use percentage
elif self.discount_amount:
    # Use fixed amount
```

### 2. Zero/Negative Price After Discount
**Scenario:** Discount amount > product price.

**Handling:**
```python
return max(self.price - self.discount_amount, Decimal('0'))
```

### 3. Missing Main Image
**Scenario:** Product has no `image` field set.

**Template Handling:** Should check `{% if product.image %}` before rendering.

### 4. Category with No Parent (Root Categories)
**Scenario:** Category tree display in navigation.

**Handling:** Context processor filters root categories:
```python
Category.objects.filter(parent=None)
```

### 5. Is Adjustable + Sizes Selected
**Scenario:** Admin marks product as adjustable but also assigns sizes.

**Behavior:** Frontend should hide size selector if `is_adjustable=True`.

### 6. Slug Uniqueness
**Scenario:** Two products with same name.

**Handling:** `prepopulated_fields` suggests slug, but uniqueness must be enforced.

---

## Payment Edge Cases

### 1. bKash/Nagad Number Validation
**Constraint:** Must be exactly 11 digits, starting with "01".

**Validation Pattern:** `^01[3-9]\d{8}$`

### 2. Transaction ID Uniqueness
**Potential Issue:** Same transaction ID could be reused fraudulently.

**Improvement:** Consider unique constraint or verification step.

### 3. COD Order Cancellation
**Scenario:** Customer refuses delivery.

**Process:** Mark as Cancelled, revert stock (manual step currently).

### 4. Partial Payments
**Current State:** Not supported. Full payment assumed.

---

## API Integration Edge Cases

### 1. Pathao Token Expiration
**Scenario:** Cached token expires mid-session.

**Handling:** Token cached with 1-minute buffer before expiry:
```python
cache.set(self.TOKEN_CACHE_KEY, token, expires_in - 60)
```

### 2. Pathao API Failure
**Scenario:** Pathao API is down or returns error.

**Handling:** Error logged, exception raised with message:
```python
except requests.RequestException as e:
    logger.error(f"Failed to create parcel: {e}")
    raise Exception(f"Pathao API error: {message}")
```

**UI Impact:** Admin sees error message.

### 3. Telegram Bot Not Configured
**Scenario:** Bot token or chat ID not set in `.env`.

**Handling:** Logged warning, function returns False, order still completes:
```python
if not bot_token or not chat_id:
    logger.warning("Telegram credentials not configured")
    return False
```

### 4. Telegram Rate Limits
**Scenario:** Many orders in short time exceed Telegram API limits.

**Mitigation:** 10-second timeout, errors logged but don't block order.

### 5. Pathao Location IDs Missing
**Scenario:** Order placed but `pathao_city_id` not set.

**Handling:** Defaults applied:
```python
'recipient_city': order.pathao_city_id or 1,  # Default to Dhaka
```

---

## Template/Frontend Edge Cases

### 1. TemplateSyntaxError History
**Past Issues:** Multiple instances of unclosed template blocks.

**Root Cause:** Manual edits missing `{% endif %}` or `{% endblock %}`.

**Prevention:** Test render after every template change.

### 2. CSS Cache Issues
**Symptom:** Style changes not appearing.

**Solution:** CSS versioning implemented:
```html
<link href="{% static 'css/style.css' %}?v=23" rel="stylesheet">
```

### 3. Mobile Menu State
**Scenario:** Menu opens, user rotates device.

**Current:** JavaScript toggle, no resize handler.

### 4. Image Aspect Ratios
**Issue:** Inconsistent product images.

**Handling:** `object-fit` and `object-position` configurable per product.

### 5. Long Product Names
**Scenario:** Product name exceeds card width.

**CSS Handling:** `text-overflow: ellipsis` or word-wrap.

---

## Known Bugs & Limitations

### Critical
| ID | Issue | Status | Workaround |
|----|-------|--------|------------|
| - | None currently identified | - | - |

### Medium
| ID | Issue | Status | Workaround |
|----|-------|--------|------------|
| M1 | Stock check not validated at checkout | Open | Admin manual check |
| M2 | Guest orders not linkable to accounts | Open | Manual database update |

### Low
| ID | Issue | Status | Workaround |
|----|-------|--------|------------|
| L1 | Cart items for deleted products silently disappear | Open | N/A |
| L2 | Variant stock not synced to front-end dynamically | Open | Page refresh needed |

---

## Test Scenarios

### Cart Tests
- [ ] Add product without variants
- [ ] Add product with size only
- [ ] Add product with color only
- [ ] Add product with size and color
- [ ] Add same product with different variants
- [ ] Remove specific variant from cart
- [ ] Update quantity to 0
- [ ] View cart with deleted product

### Checkout Tests
- [ ] Guest checkout with all fields
- [ ] Guest checkout missing required fields
- [ ] Logged-in checkout with pre-filled fields
- [ ] bKash payment without transaction ID
- [ ] Nagad payment with transaction ID
- [ ] COD payment
- [ ] Checkout with zero stock product

### Order Tests
- [ ] Order creation decrements stock
- [ ] Telegram notification sent
- [ ] Order linked to logged-in user
- [ ] Guest order has null user
- [ ] Pathao consignment creation

---

## Error Handling Patterns

### View Level
```python
try:
    # Risky operation
except Exception as e:
    messages.error(request, "An error occurred")
    logger.error(f"Error: {e}")
```

### API Level
```python
try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API call failed: {e}")
    return None  # or raise custom exception
```

### Template Level
```django
{% if product.image %}
    <img src="{{ product.image.url }}" />
{% else %}
    <img src="{% static 'img/placeholder.png' %}" />
{% endif %}
```
