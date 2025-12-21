import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from store.models import Theme

themes_data = [
    {
        "name": "Earthy and Serene",
        "primary_color": "#865D36",
        "text_color": "#3E352E",
        "bg_color": "#A69080",
        "accent_color": "#93785B",
        "promo_bg": "#AC8968",
        "is_active": True
    },
    {
        "name": "Cool and Collected",
        "primary_color": "#003135",
        "text_color": "#024950",
        "bg_color": "#AFDDE5",
        "accent_color": "#0FA4AF",
        "promo_bg": "#964734",
        "is_active": False
    },
    {
        "name": "Red and Lively",
        "primary_color": "#9A1750",
        "text_color": "#5D001E",
        "bg_color": "#E3E2DF",
        "accent_color": "#EE4C7C",
        "promo_bg": "#E3AFBC",
        "is_active": False
    }
]

for data in themes_data:
    theme, created = Theme.objects.get_or_create(
        name=data['name'],
        defaults={
            "primary_color": data["primary_color"],
            "text_color": data["text_color"],
            "bg_color": data["bg_color"],
            "accent_color": data["accent_color"],
            "promo_bg": data["promo_bg"],
            "is_active": data["is_active"]
        }
    )
    if not created:
        # Update existing check if we want to reset colors? 
        # For now let's just update defaults if needed or leave as is.
        # User might have customized it. Let's strictly update if script run manually?
        # Let's act like a seed script and valid fields.
        if data['is_active']:
            # If we run this script and set Earthy as active, it will de-activate others due to save()
            theme.is_active = True
            theme.save()
            print(f"Set active: {theme.name}")
        else:
            print(f"Exists: {theme.name}")
    else:
        print(f"Created: {theme.name}")
