from django.urls import path
from . import views


app_name = 'store'


urlpatterns = [
    # This routes the empty path (the website's root) to the product_list view
    path('', views.product_list, name='product_list'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist_list, name='wishlist_list'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'), # <--- And this name
]