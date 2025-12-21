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

## Entry 5:

Action: Implemented Global Cart Context Processor.

Changes: Created cart/context_processors.py, updated settings.py, and updated base.html to show the dynamic cart count.

## Entry 6: Started Phase 3 (Orders). Initialized orders app and defining Order models.

## Entry 7: Implemented Checkout Logic. Created Admin, Forms, Views, and URLs for orders app.

## Entry 8: Action: Completed Phase 3. Created Checkout and Success templates. Validated full purchase flow.

## Entry 9: Started Phase 4 (Authentication). Initialized accounts app.

## Entry 10: Created Authentication Templates (login.html, register.html) and updated Navbar for dynamic user state.

## Entry 11: Linked Orders to Users and created User Dashboard. Completed Phase 4

## [Date] Fixed Order Success Page
- **Issue:** NoReverseMatch in `orders/created.html`.
- **Fix:** Updated the 'Continue Shopping' link to use the namespaced URL `{% url 'store:product_list' %}`.
- **Status:** Order flow is now fully functional from Add to Cart -> Checkout -> Success.

## [Date] Added Local Payment Methods
- **Feature:** Implemented Cash on Delivery (COD), bKash, and Nagad support.
- **Changes:**
    - Modified `Order` model to include `payment_method` and `transaction_id`.
    - Updated `OrderCreateForm` to use Radio Select widgets.
    - Updated `create.html` with JavaScript to toggle Transaction ID fields based on selection.
- **Status:** Users can now place orders with local payment context.


## Entry 12:

Action: Optimized Product Image Display.

Changes: Updated `static/css/style.css` to change the `object-fit` property for product list images (`.product-card img`) from `contain` to `cover`. This ensures images fill their designated space completely (250px height), resolving the issue of excessive whitespace that made the product look "too much zoom in" within the card. The detail view image settings (`.detail-img`) were also cleaned up but remain `object-fit: contain` to preserve the full product view.

## Entry 15:
Action: Resolved CSS Conflict and Fixed Image Sizing.
Findings: Discovered a duplicate CSS file in `store/static/css/` that was overriding the main stylesheet.
Resolution: 
- Deleted the conflicting file `store/static/css/style.css`.
- Updated `static/css/style.css` to use `object-fit: contain` and specific width/height constraints.
- Confirmed images now display fully without cropping or excessive zooming.

## Entry 17:
Action: Implemented Manual Payment Frontend.
Changes: 
- Updated `orders/templates/orders/order/create.html` with JavaScript to toggle payment fields.
- Added instructions for bKash/Nagad payments.
- Completed Phase 5 (Payment Gateway Integration - Manual Method).

## Entry 18:
Action: Major UI Overhaul & Checkout Fix.
Changes:
- Rewrote `static/css/style.css` with a premium design system (Outfit font, deep brown/gold palette, utility classes).
- Refactored `store/templates/store/product_list.html` to remove inline styles and use new components.
- Refactored `orders/templates/orders/order/create.html` to fix a template syntax error and apply the new checkout layout.
- Verified checkout page rendering.
Status: Application has a polished, premium look and checkout is functional.

## Entry 19:
Action: Bulgari-inspired Redesign.
Changes:
- Implemented "Luxe Gems" design system based on Bulgari analysis.
- Updated `base.html` header structure to include:
    - Top dark promo bar.
    - Split utility navigation (Search/Contact Left, Account/Bag Right).
    - Centered minimal Logo.
    - Dedicated clean Navigation row below logo.
- Updated `style.css`:
    - Switched font to **Montserrat** (Uppercase, spaced) for luxury feel.
    - Set primary background to white, text to black.
    - Removed shadows and rounded corners for a sharp, modern luxury aesthetic.
- Cache-busted CSS to ensure updates propagate.
Status: Homepage successfully reflects the new premium minimalist design.

## Entry 20:
Action: Fox Animated Background.
Changes:
- Generated high-res luxury "Fox in Winter Forest" illustration (`hero_bg.png`) in the style of Van Cleef & Arpels.
- Implemented `Hero Section` in `product_list.html` visible on the homepage.
- Added CSS `keyframe` animation (`kenBurns`) to create a slow, cinematic zoom/pan effect for the "animated" feel.
- Optimized hero text overlay for readability.
Status: Functional animated background implemented.

## Entry 21:
Action: Rebranding to Foxy Glamour & Enhancements.
Changes:
- **Rebranding**: Updated site name from "Luxe Gems" to "**Foxy Glamour**" in Header, Hero Section, and Page Titles.
- **Mega Menu Implementation**:
    - Updated `Category` model to include a `parent` field (self-referential ForeignKey) for subcategories.
    - Created `store.context_processors.categories` to provide specific hierarchy context globally.
    - Updated `base.html` to render a recursive dropdown menu for subcategories on hover.
    - Added CSS for smooth dropdown animations.
- **Contact Us Page**:
    - Designed and implemented a new standard "Contact Us" page (`/contact/`).
    - Features clean, minimalist cards for Facebook, Instagram, and Email.
    - Linked from the Header utility bar.
Status: Rebranding complete, Mega Menu architecture ready for data, Contact page live.

## Entry 22:
Action: Updated Contact Information.
Changes:
- Updated Social Media links on the Contact Us page (`contact.html`) with user-provided URLs:
    - **Instagram**: `https://www.instagram.com/foxyglamourbd2/`
    - **Facebook**: `https://www.facebook.com/profile.php?id=61583188543696`
Status: Contact links functional and accurate.

## Entry 23:
Action: Brand Identity - SVG Logo.
Changes:
- Integrated user-provided SVG logo (`Logo.svg`).
- Replaced the "Foxy Glamour" text logo in the **Header** with the SVG.
- Replaced the "Foxy Glamour" text heading in the **Hero Section** with a white version of the SVG (using CSS filter).
Status: Logo successfully implemented across key brand touchpoints.

## Entry 24:
Action: Server Restart.
Changes:
- Copied updated `Logo.svg` from source to static directory.
- Restarted Django development server to ensure all static assets are refreshed.
Status: Deployment successfully verified.
