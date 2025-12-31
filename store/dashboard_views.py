from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F, Count
from django.utils import timezone
from orders.models import Order, OrderItem
from .models import Product, Visitor

@staff_member_required
def admin_dashboard(request):
    # Overall Order Stats
    total_orders = Order.objects.count()
    
    # Financials
    # Calculate revenue from OrderItems to accuracy (price * quantity)
    items = OrderItem.objects.all()
    total_revenue = sum(item.price * item.quantity for item in items)
    
    # COGS (Cost of Goods Sold)
    total_cost = 0
    for item in items:
        cost = item.cost_price if item.cost_price is not None else item.product.cost_price
        total_cost += cost * item.quantity

    # Net Profit
    net_profit = total_revenue - total_cost

    # Recent Orders
    recent_orders = Order.objects.select_related('user').order_by('-created')[:10]
    
    # Customer Activity (Top Customers by Order Count)
    top_customers = Order.objects.values('email').annotate(order_count=Count('id')).order_by('-order_count')[:5]

    # --- VISITOR METRICS ---
    # Total unique visitors today (by IP)
    today = timezone.now().date()
    visitors_today = Visitor.objects.filter(created__date=today).values('ip_address').distinct().count()
    
    # Top Traffic Sources (utm_source)
    top_sources = Visitor.objects.values('utm_source').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Recent Visits
    recent_visits = Visitor.objects.order_by('-created')[:10]
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'net_profit': net_profit,
        'recent_orders': recent_orders,
        'top_customers': top_customers,
        'visitors_today': visitors_today,
        'top_sources': top_sources,
        'recent_visits': recent_visits,
    }
    
    return render(request, 'store/dashboard.html', context)
