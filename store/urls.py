
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    path(
        'add-to-cart/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),

    path('cart/', views.cart, name='cart'),

    path(
        'remove-from-cart/<int:product_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'increase/<int:product_id>/',
        views.increase_quantity,
        name='increase_quantity'
    ),

    path(
        'decrease/<int:product_id>/',
        views.decrease_quantity,
        name='decrease_quantity'
    ),

    path('checkout/', views.checkout, name='checkout'),

    path('order-success/', views.order_success, name='order_success'),
]
