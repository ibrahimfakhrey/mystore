from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index,name='index'),
    path('product/<int:id>',views.detail,name='detail'),
      path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart',views.cart, name='cart'),
        path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
path('success',views.payment_sucess_view,name='success'),
path('failed',views.payment_failed_view,name='failed'),
path('api/checkout-session/<int:id>/',views.create_checkout_session,name='api_checkout_session'),
]
