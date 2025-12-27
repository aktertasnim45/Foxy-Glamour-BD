from django.shortcuts import render, get_object_or_404
import json
from .models import Category, Product
from cart.forms import CartAddProductForm
from django.db.models import Q

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Category Filter
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search Filter (Name or Description)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass # Ignore invalid input
            
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass # Ignore invalid input

    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else: # newest
        products = products.order_by('-created')

    # Helper to generate sort URLs
    def get_sort_url(sort_value):
        params = request.GET.copy()
        params['sort'] = sort_value
        return f"?{params.urlencode()}"

    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'sort_by': sort_by,
        'is_newest': sort_by == 'newest',
        'is_price_asc': sort_by == 'price_asc',
        'is_price_desc': sort_by == 'price_desc',
        'url_newest': get_sort_url('newest'),
        'url_price_asc': get_sort_url('price_asc'),
        'url_price_desc': get_sort_url('price_desc'),
    })

def contact(request):
    return render(request, 'store/contact.html')

def about(request):
    return render(request, 'store/about.html')


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()

    # Related Products (Same category, excluding current)
    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]

    # Serialize variants for frontend logic
    variants_data = []
    if product.variants.exists():
        for v in product.variants.all():
            variants_data.append({
                'size': v.size.code if v.size else 'Adjustable', # Assuming 'Adjustable' or None map to null/string
                'color': v.color.code if v.color else None,
                'stock': v.stock
            })
            
    return render(request, 'store/product_detail.html', {
        'product': product, 
        'cart_product_form': cart_product_form,
        'related_products': related_products,
        'variants_json': json.dumps(variants_data)
    })

def search(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    metal = request.GET.get('metal')
    sort_by = request.GET.get('sort', 'newest') # newest, price_asc, price_desc

    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    # Base Search
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(gemstone__icontains=query) |
            Q(metal__icontains=query)
        )
    
    # Filters
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
            
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if metal:
         products = products.filter(metal=metal)

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created')

    # Get distinct metals for filter sidebar
    metals = Product.objects.values_list('metal', flat=True).distinct().exclude(metal='')

    context = {
        'products': products,
        'categories': categories,
        'metals': metals,
        'query': query,
        'sort_by': sort_by,
        'is_newest': sort_by == 'newest',
        'is_price_asc': sort_by == 'price_asc',
        'is_price_desc': sort_by == 'price_desc',
    }
    return render(request, 'store/search_fixed.html', context)


from django.contrib.auth.decorators import login_required
from .models import Wishlist
from django.shortcuts import redirect

@login_required
def wishlist_list(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('store:wishlist_list')

@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect('store:wishlist_list')
