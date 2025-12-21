"""
Telegram Bot Notification Service

Send order notifications to Telegram when new orders are placed.
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(message):
    """
    Send a message to Telegram bot
    
    Args:
        message: Text message to send
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
    
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


def send_order_notification(order):
    """
    Send a formatted order notification to Telegram
    
    Args:
        order: Order model instance
    """
    # Build item list
    items_text = ""
    for item in order.items.all():
        items_text += f"  • {item.product.name} x{item.quantity} = ৳{item.get_cost()}\n"
    
    # Build the message
    message = f"""
🛒 <b>New Order #{order.id}</b>

👤 <b>Customer:</b>
{order.first_name} {order.last_name}
📞 {order.phone}
{"📧 " + order.email if order.email else ""}

📍 <b>Address:</b>
{order.address}
{order.city}, {order.postal_code}
🚚 {order.get_shipping_zone_display()}

📦 <b>Items:</b>
{items_text}
💰 <b>Subtotal:</b> ৳{sum(item.get_cost() for item in order.items.all())}
🚚 <b>Shipping:</b> ৳{order.get_shipping_cost()}
💵 <b>Total:</b> ৳{order.get_total_cost()}

💳 <b>Payment:</b> {order.get_payment_method_display()}
{"🔢 TxID: " + order.transaction_id if order.transaction_id else ""}

⏰ {order.created.strftime('%d %b %Y, %I:%M %p')}
"""
    
    return send_telegram_message(message.strip())
