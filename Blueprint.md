# Project Blueprint: Foxy Glamour BD (Jewelry Site)

## Project Overview
A Django-based e-commerce platform for selling jewelry, focusing on elegance and user experience.

## Architecture
- **Framework**: Django 5.2.8
- **Database**: SQLite (Development)
- **Styling**: Custom CSS (currently `style.css`)
- **State Management**: Django Sessions (for Shopping Cart)

## Roadmap

### Phase 1: Core Setup & Product Catalog [COMPLETED]
- [x] Project Initialization (`jewelry_site`)
- [x] Store App Configuration
- [x] Product & Category Models
- [x] Basic Views (List & Detail)
- [x] Basic Templates & Static Files

### Phase 2: Shopping Cart Logic [CURRENT FOCUS]
- [x] Create `cart` app.
- [x] Implement Session-based Cart class.
- [x] Create views to Add/Remove items.
- [x] Build Cart Summary page.
- [x] Update Navbar with Cart counter.

### Phase 3: Checkout & Orders [COMPLETED]
- [x] Create `orders` app.
- [x] Define `Order` models.
- [x] Implement Checkout Logic.
- [x] Success Page & Admin Integration.

### Phase 4: User Authentication [CURRENT FOCUS]
- [ ] Initialize `accounts` app.
- [ ] User Registration (Sign Up).
- [ ] User Login/Logout.
- [ ] Navbar updates (Show "Login" vs "Logout").
- [ ] User Dashboard (Order History).