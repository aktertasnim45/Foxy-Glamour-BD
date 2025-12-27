from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Product, Category

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['store:product_list', 'store:about', 'store:contact']

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return Product.objects.filter(available=True)

    def lastmod(self, obj):
        return obj.updated

class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Category.objects.all()
