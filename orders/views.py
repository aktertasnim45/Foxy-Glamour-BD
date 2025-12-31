from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .telegram import send_order_notification

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # CHANGE STARTS HERE
            order = form.save(commit=False) # Create the object but don't save to DB yet
            
            if request.user.is_authenticated: # If the user is logged in
                order.user = request.user     # Attach the user to the order
            
            # Apply mobile payment discount for bKash/Nagad
            from .models import Order
            if order.payment_method in ['bkash', 'nagad']:
                order.payment_discount = Order.MOBILE_PAYMENT_DISCOUNT
            
            order.save() # Now save it to DB
            # CHANGE ENDS HERE
            
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         cost_price=item['product'].cost_price,
                                         quantity=item['quantity'])
                # Decrement Stock
                product = item['product']
                product.stock -= item['quantity']
                if product.stock < 0:
                    product.stock = 0 # Prevent negative stock (safety)
                product.save()
            
            # Send Telegram notification
            try:
                send_order_notification(order)
            except Exception:
                pass  # Don't fail order if notification fails
            
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