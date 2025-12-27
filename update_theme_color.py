import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from store.models import Theme

themes = Theme.objects.all()
if themes.count() == 0:
    print("No themes found! Creating a default theme.")
    Theme.objects.create(name="Default", promo_bg="#97a6f7")
else:
    print(f"Found {themes.count()} themes.")
    for theme in themes:
        print(f"Updating theme '{theme.name}' (current promo_bg: {theme.promo_bg})")
        theme.promo_bg = '#97a6f7'
        theme.save()
        print(f"Updated theme '{theme.name}' to promo_bg: {theme.promo_bg}")
