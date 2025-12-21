"""
Pathao Courier API Integration Service

This module handles all interactions with the Pathao Courier API including:
- Authentication and token management
- Fetching cities, zones, and areas
- Creating parcels
- Tracking order status
"""

import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PathaoClient:
    """Client for interacting with Pathao Courier API"""
    
    TOKEN_CACHE_KEY = 'pathao_access_token'
    TOKEN_CACHE_TIMEOUT = 3600  # 1 hour (tokens typically last longer but refresh often)
    
    def __init__(self):
        self.base_url = getattr(settings, 'PATHAO_BASE_URL', 'https://api-hermes.pathao.com')
        self.client_id = getattr(settings, 'PATHAO_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'PATHAO_CLIENT_SECRET', '')
        self.client_email = getattr(settings, 'PATHAO_CLIENT_EMAIL', '')
        self.client_password = getattr(settings, 'PATHAO_CLIENT_PASSWORD', '')
        self.store_id = getattr(settings, 'PATHAO_STORE_ID', '')
    
    def _get_token(self):
        """Get access token, using cache if available"""
        token = cache.get(self.TOKEN_CACHE_KEY)
        if token:
            return token
        
        # Request new token
        url = f"{self.base_url}/aladdin/api/v1/issue-token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'username': self.client_email,
            'password': self.client_password,
            'grant_type': 'password'
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            token = data.get('access_token')
            
            # Cache the token
            if token:
                expires_in = data.get('expires_in', self.TOKEN_CACHE_TIMEOUT)
                cache.set(self.TOKEN_CACHE_KEY, token, expires_in - 60)  # Refresh 1 min early
            
            return token
        except requests.RequestException as e:
            logger.error(f"Failed to get Pathao access token: {e}")
            raise Exception(f"Pathao authentication failed: {e}")
    
    def _get_headers(self):
        """Get headers with authorization"""
        token = self._get_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_cities(self):
        """Fetch list of available cities"""
        url = f"{self.base_url}/aladdin/api/v1/countries/1/city-list"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('data', {}).get('data', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch cities: {e}")
            return []
    
    def get_zones(self, city_id):
        """Fetch zones for a city"""
        url = f"{self.base_url}/aladdin/api/v1/cities/{city_id}/zone-list"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('data', {}).get('data', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch zones for city {city_id}: {e}")
            return []
    
    def get_areas(self, zone_id):
        """Fetch areas for a zone"""
        url = f"{self.base_url}/aladdin/api/v1/zones/{zone_id}/area-list"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('data', {}).get('data', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch areas for zone {zone_id}: {e}")
            return []
    
    def get_stores(self):
        """Fetch list of stores"""
        url = f"{self.base_url}/aladdin/api/v1/stores"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('data', {}).get('data', [])
        except requests.RequestException as e:
            logger.error(f"Failed to fetch stores: {e}")
            return []
    
    def create_parcel(self, order):
        """
        Create a parcel/order in Pathao system
        
        Args:
            order: Order model instance
            
        Returns:
            dict: Response from Pathao API with consignment_id
        """
        url = f"{self.base_url}/aladdin/api/v1/orders"
        
        # Build item description from order items
        item_descriptions = []
        total_quantity = 0
        for item in order.items.all():
            item_descriptions.append(f"{item.product.name} x{item.quantity}")
            total_quantity += item.quantity
        
        # Calculate amount to collect (total cost for COD)
        amount_to_collect = float(order.get_total_cost()) if order.payment_method == 'cod' else 0
        
        payload = {
            'store_id': int(self.store_id),
            'merchant_order_id': str(order.id),
            'sender_name': getattr(settings, 'PATHAO_SENDER_NAME', 'Foxy Glamour'),
            'sender_phone': getattr(settings, 'PATHAO_SENDER_PHONE', ''),
            'recipient_name': f"{order.first_name} {order.last_name}".strip(),
            'recipient_phone': order.phone,
            'recipient_address': order.address,
            'recipient_city': order.pathao_city_id or 1,  # Default to Dhaka (1)
            'recipient_zone': order.pathao_zone_id or 1,
            'recipient_area': order.pathao_area_id or 1,
            'delivery_type': 48,  # Normal delivery (48 hours)
            'item_type': 2,  # Parcel
            'special_instruction': f"Order #{order.id}",
            'item_quantity': total_quantity,
            'item_weight': 0.5,  # Default weight in kg
            'amount_to_collect': amount_to_collect,
            'item_description': ', '.join(item_descriptions)[:500],  # Max 500 chars
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            # Update order with Pathao response
            if data.get('type') == 'success':
                order_data = data.get('data', {})
                order.pathao_consignment_id = order_data.get('consignment_id')
                order.pathao_order_status = order_data.get('order_status', 'Pending')
                order.sent_to_pathao = True
                order.save()
                
            return data
        except requests.RequestException as e:
            logger.error(f"Failed to create parcel for order {order.id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Pathao error response: {error_data}")
                    raise Exception(f"Pathao API error: {error_data.get('message', str(e))}")
                except ValueError:
                    pass
            raise Exception(f"Failed to create Pathao parcel: {e}")
    
    def get_order_status(self, consignment_id):
        """
        Get order/parcel status from Pathao
        
        Args:
            consignment_id: Pathao consignment ID
            
        Returns:
            dict: Order status information
        """
        url = f"{self.base_url}/aladdin/api/v1/orders/{consignment_id}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get order status for {consignment_id}: {e}")
            return None


# Default city/zone mappings for Bangladesh
# These are commonly used IDs - you may need to update based on your Pathao account
PATHAO_CITY_MAPPINGS = {
    'dhaka': 1,
    'chittagong': 2,
    'chattogram': 2,
    'rajshahi': 3,
    'khulna': 4,
    'sylhet': 5,
    'rangpur': 6,
    'barisal': 7,
    'mymensingh': 8,
}

# Zone IDs for Dhaka (example - verify with actual API)
PATHAO_DHAKA_ZONES = {
    'inside_dhaka': 1,      # Central Dhaka
    'intercity_dhaka': 2,   # Greater Dhaka
    'outside_dhaka': None,  # Outside Dhaka - need to set city
}


def get_city_id_from_name(city_name):
    """Helper to get city ID from city name"""
    if not city_name:
        return 1  # Default to Dhaka
    
    city_lower = city_name.lower().strip()
    return PATHAO_CITY_MAPPINGS.get(city_lower, 1)
