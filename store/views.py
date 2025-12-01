from django.shortcuts import render, get_object_or_404
from .models import Product
from cart.forms import CartAddProductForm  # <-- Import the form

def product_list(request):
    products = Product.objects.filter(is_available=True) 
    context = {
        'products': products
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    
    # Create an instance of the form to allow users to select quantity
    cart_product_form = CartAddProductForm()

    context = {
        'product': product,
        'cart_product_form': cart_product_form # <-- Add form to context
    }
    return render(request, 'store/product_detail.html', context)