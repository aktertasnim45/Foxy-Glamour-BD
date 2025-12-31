import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

def verify_visits():
    c = Client()
    
    # 1. Visit Home (No UTM)
    c.get('/', HTTP_USER_AGENT='Mozilla/5.0 Test')

    # 2. Visit Product (Facebook Ad)
    c.get('/?utm_source=facebook&utm_medium=cpc&utm_campaign=winter_sale', 
          HTTP_USER_AGENT='Mozilla/5.0 iPhone',
          HTTP_REFERER='https://facebook.com')

    # 3. Visit Cart (Google Organic)
    c.get('/cart/?utm_source=google&utm_medium=organic',
          HTTP_USER_AGENT='Mozilla/5.0 Android',
          HTTP_REFERER='https://google.com')

    # Verify DB
    from store.models import Visitor
    count = Visitor.objects.filter(utm_source='facebook').count()
    print(f"Facebook visits: {count}")
    
    count_all = Visitor.objects.count()
    print(f"Total visits recorded: {count_all}")
    
    if count >= 1 and count_all >= 3:
        print("✓ Tracking Logic: PASSED")
    else:
        print("x Tracking Logic: FAILED")

if __name__ == '__main__':
    verify_visits()
