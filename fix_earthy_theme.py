import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from store.models import Theme

# Correct values for Earthy and Serene
theme = Theme.objects.get(name="Earthy and Serene")
theme.primary_color = "#865D36" # Brown
theme.text_color = "#3E352E"    # Dark Brown
theme.bg_color = "#A69080"      # Taupe
theme.accent_color = "#93785B"  # Beige
theme.promo_bg = "#AC8968"      # Light Brown
theme.is_active = True
theme.save()
print(f"Updated {theme.name} colors.")
