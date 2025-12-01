# Project Journal

## Entry 1: Project Analysis & Planning
- **Date**: 2025-12-01
- **Action**: Reviewed existing codebase.
- **Findings**: 
    - Basic catalog (Models, Views, URLs) is functional. 
    - `Add to Cart` button exists but is non-functional.
    - Media settings are configured correctly.
- **Decision**: Priority is to implement the Shopping Cart functionality using a new Django app called `cart`.
# Project Journal

## Entry 1: Phase 2 Initialization
- **Date**: 2025-12-02
- **Action**: Started Phase 2 (Shopping Cart).
- **Changes**: 
    - Created `Blueprint.md` and `Journal.md`.
    - Initialized `cart` app.
    - Updated `settings.py` to include `cart` and `CART_SESSION_ID`.
    - Created `cart/cart.py` for session handling logic.

## Entry 2: Implemented Cart Views and Forms. Created cart/forms.py, cart/views.py, and cart/urls.py.

## Entry 3: Action: Wired up Cart URLs and created the Cart Detail template. Files: Modified jewelry_site/urls.py, Created cart/templates/cart/detail.html.

## Entry 4:
Action: Connected Product Detail view to Cart logic.
Changes: Updated store/views.py to inject CartAddProductForm. Updated store/templates/store/product_detail.html to render the form.