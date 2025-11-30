from django.urls import path
from . import views

urlpatterns = [
    # This routes the empty path (the website's root) to the product_list view
    path('', views.product_list, name='product_list'),
    path('<slug:product_slug>/', views.product_detail, name='product_detail'),
]