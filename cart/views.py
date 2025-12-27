from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from store.models import Product, Size, Color, ProductVariant
from .cart import Cart
from .forms import CartAddProductForm

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        
        # Enforce "Adjustable" size for adjustable products
        size_to_add = cd.get('size')
        if product.is_adjustable:
            size_to_add = "Adjustable"
            
        color_to_add = cd.get('color')

        # Variation Stock Logic
        variant = None
        stock_limit = product.stock
        
        # Try to find specific variant
        if product.variants.exists():
            try:
                # Resolve Size object (handle 'Adjustable' or None)
                s_obj = None
                if size_to_add and size_to_add != 'Adjustable':
                    s_obj = Size.objects.filter(code=size_to_add).first()
                
                # Resolve Color object
                c_obj = None
                if color_to_add:
                    c_obj = Color.objects.filter(code=color_to_add).first()

                # Look for exact variant match
                variant = ProductVariant.objects.filter(product=product, size=s_obj, color=c_obj).first()
                
                if variant:
                    stock_limit = variant.stock
            except Exception as e:
                # Fallback to global stock if something fails
                pass

        # Calculate current quantity of this specific variation in cart
        current_quantity = 0
        for item in cart:
            if str(item['product'].id) == str(product.id):
                # If we found a variant, only count items matching this variation
                if variant:
                    if item.get('size') == size_to_add and item.get('color') == color_to_add:
                        current_quantity += item['quantity']
                else:
                     # Legacy/Global Check: Count all items of this product
                    current_quantity += item['quantity']

        # Check stock limit
        if not cd['override']:
            if current_quantity + cd['quantity'] > stock_limit:
                messages.warning(request, f'Sorry, only {stock_limit} items are available in this variation. You already have {current_quantity} in your cart.')
                return redirect('store:product_detail', id=product.id, slug=product.slug)
        else:
            # For override (update quantity in cart), we need to be careful.
            # current_quantity includes the old quantity of the item being updated.
            # We need to find the specific item being updated to subtract its old quantity.
            
            old_qty_of_this_item = 0
            for item in cart:
                 # Standardize comparison
                 item_size = item.get('size')
                 item_color = item.get('color')
                 
                 if str(item['product'].id) == str(product.id) and item_size == size_to_add and item_color == color_to_add:
                     old_qty_of_this_item = item['quantity']
                     break
            
            new_total = (current_quantity - old_qty_of_this_item) + cd['quantity']
            if new_total > stock_limit:
                messages.warning(request, f'Sorry, you cannot add that amount. Only {stock_limit} items are available.')
                # If updating from cart detail, we usually redirect to cart_detail
                return redirect('cart:cart_detail')

        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'],
                 size=size_to_add,
                 color=color_to_add)
    else:
        # Debugging: Print errors to console
        print(f"Cart Add Form Errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error in {field}: {error}")
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size')
    color = request.POST.get('color')
    cart.remove(product, size=size, color=color)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True
        })
    return render(request, 'cart/detail.html', {'cart': cart})