"""
Test script for Pathao API integration
Run this from the project root: python test_pathao.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from orders.pathao import PathaoClient
from django.conf import settings

def test_pathao():
    print("=" * 50)
    print("PATHAO API TEST")
    print("=" * 50)
    
    # Check if credentials are loaded
    print("\n1. Checking credentials...")
    if not settings.PATHAO_CLIENT_ID:
        print("   ERROR: PATHAO_CLIENT_ID is empty!")
        return
    print(f"   Client ID: {settings.PATHAO_CLIENT_ID[:10]}...")
    print(f"   Store ID: {settings.PATHAO_STORE_ID}")
    print(f"   Email: {settings.PATHAO_CLIENT_EMAIL}")
    print("   ✓ Credentials loaded from .env")
    
    # Test API connection
    print("\n2. Testing API authentication...")
    client = PathaoClient()
    
    try:
        cities = client.get_cities()
        print(f"   ✓ SUCCESS! Connected to Pathao API")
        print(f"   Found {len(cities)} cities")
        
        print("\n3. City List (first 10):")
        for city in cities[:10]:
            print(f"   ID {city.get('city_id'):3}: {city.get('city_name')}")
        
        # Test zones for Dhaka
        print("\n4. Testing zones for Dhaka (city_id=1)...")
        zones = client.get_zones(1)
        print(f"   Found {len(zones)} zones in Dhaka")
        print("   Sample zones:")
        for zone in zones[:5]:
            print(f"   ID {zone.get('zone_id'):4}: {zone.get('zone_name')}")
            
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pathao()
