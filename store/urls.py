from django.urls import path
from . import views


app_name = 'store'


urlpatterns = [
    # This routes the empty path (the website's root) to the product_list view
    path('', views.product_list, name='product_list'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'), # <--- And this name
]