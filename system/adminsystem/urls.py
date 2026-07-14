from django.urls import path
from . import views

urlpatterns = [
    # 1. ទំព័រដើម (Home Page / Index)
    path('', views.index, name='index'), 
    
    # 2. ប្រព័ន្ធគ្រប់គ្រងគណនី (Authentication System)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    
    # 3. ទំព័រមើលបញ្ជីឈ្មោះអ្នកប្រើប្រាស់ (សម្រាប់តែ Superadmin)
    path('check-users/', views.user_list_view, name='user_list'),
    
    # 4. ផ្លូវទៅកាន់ទំព័រហាងនីមួយៗ និងបង្ហាញផលិតផលក្នុងហាងនោះ (Shop Detail)
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('place-order/', views.place_order, name='place_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('admin-dashboard/orders/', views.admin_orders_view, name='admin_orders'),
    path('admin-dashboard/orders/<int:order_id>/accept/', views.admin_accept_order, name='admin_accept_order'),
    path('admin-dashboard/orders/<int:order_id>/complete/', views.admin_complete_order, name='admin_complete_order'),
    path('admin_order', views.admin_orders_view, name='admin_orders_shortcut'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('admin-dashboard/orders/<int:order_id>/cancel/', views.admin_cancel_order, name='admin_cancel_order'),
    path('about-us/', views.about_us, name='about_us'),
]