from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm  # <-- Import the form

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    context = {'category': category, 'categories': categories, 'products': products}
    return render(request, 'store/product_list.html', context)

def product_detail(request, id, slug):
    # We retrieve the product using both ID and slug for SEO-friendly URLs that are also unique
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    # If you have a cart form (based on your previous HTML file), initialize it here:
    cart_product_form = CartAddProductForm()
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form, # Uncomment if you have the form
    }
    return render(request, 'store/product_detail.html', context)

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False) # Create object but don't save to DB yet
            
            if request.user.is_authenticated:
                order.user = request.user # Link the logged-in user
                
            order.save() # Now save it
            
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            return render(request, 'orders/order/created.html',
                          {'order': order})
    else:
        # Pre-fill form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
        
    return render(request, 'orders/order/create.html',
                  {'cart': cart, 'form': form})