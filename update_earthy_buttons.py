import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from store.models import Theme

# Update Earthy theme to use its palette for buttons
theme = Theme.objects.get(name="Earthy and Serene")
# Add to Cart (Primary Button) -> Earthy Brown
theme.button_bg_color = "#865D36" 
theme.button_text_color = "#FFFFFF"
theme.button_hover_bg_color = "#3E352E" # Darker Brown

# Buy Now (Secondary Button) -> White with Brown text
theme.buy_now_bg_color = "#FFFFFF"
theme.buy_now_text_color = "#865D36" 
theme.buy_now_hover_bg_color = "#865D36"
theme.buy_now_hover_text_color = "#FFFFFF"

theme.save()
print(f"Updated {theme.name} button colors.")
