from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Create the order object but DO NOT save to database yet
            order = form.save(commit=False)
            
            # 2. Check if user is logged in
            if request.user.is_authenticated:
                order.user = request.user # Attach the user to the order
                
            # 3. Now save the order to the database
            order.save()
            
            # 4. Save the items
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # 5. Clear cart
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