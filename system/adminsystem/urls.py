from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'), 

    path('logout/', views.logout_view, name='logout'),
    path('check-users/', views.user_list_view, name='user_list'),
   
    
    
]