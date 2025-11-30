from django.shortcuts import render,get_object_or_404
from .models import Product # Import your Product model

def product_list(request):
    # Fetch all products that are marked as available
    products = Product.objects.filter(is_available=True) 

    # Prepare the context (data) to send to the template
    context = {
        'products': products
    }

    # Render the 'store/product_list.html' template with the product data
    return render(request, 'store/product_list.html', context)
# Create your views here.
def product_detail(request, product_slug):
    # Tries to get the product, or shows a 404 page if not found
    product = get_object_or_404(Product, slug=product_slug, is_available=True)

    context = {
        'product': product
    }
    return render(request, 'store/product_detail.html', context)