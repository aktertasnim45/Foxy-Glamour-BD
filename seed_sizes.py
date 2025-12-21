import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from store.models import Size

sizes = [
    {'name': '6', 'code': '6'},
    {'name': '7', 'code': '7'},
    {'name': '8', 'code': '8'},
    {'name': '9', 'code': '9'},
]

for s in sizes:
    obj, created = Size.objects.get_or_create(code=s['code'], defaults={'name': s['name']})
    if created:
        print(f"Created Size: {s['name']}")
    else:
        print(f"Size already exists: {s['name']}")
