from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from store.models import Product
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

        # Calculate current quantity of this product in cart
        current_quantity = 0
        for item in cart:
            if str(item['product'].id) == str(product.id):
                current_quantity += item['quantity']

        # Check stock limit
        if not cd['override']:
            if current_quantity + cd['quantity'] > product.stock:
                messages.warning(request, f'Sorry, only {product.stock} items are available. You already have {current_quantity} in your cart.')
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
            if new_total > product.stock:
                messages.warning(request, f'Sorry, you cannot add that amount. Only {product.stock} items are available in total.')
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