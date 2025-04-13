# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:pk>/update/', views.client_update, name='client_update'),
    path('clients/<int:pk>/delete/', views.client_delete, name='client_delete'),

    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/update/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('productmolds/', views.productmold_list, name='productmold_list'),
    path('productmolds/create/', views.productmold_create, name='productmold_create'),
    path('productmolds/<int:pk>/update/', views.productmold_update, name='productmold_update'),
    path('productmolds/<int:pk>/delete/', views.productmold_delete, name='productmold_delete'),

    path('trash/', views.trash_list, name='trash_list'),
    path('trash/create/', views.trash_create, name='trash_create'),
    path('trash/<int:pk>/delete/', views.trash_delete, name='trash_delete'),
    path('trash/<int:pk>/complete/', views.trash_complete, name='trash_complete'),
    path('trash/<int:pk>/', views.trash_items, name='trash_detail'),
    path('trash/<int:pk>/', views.trash_items, name='trash_items'),

    path('product_history/<int:pk>/complete/', views.product_history_complete, name='product_history_complete'),
    path('productmold_history/<int:pk>/complete/', views.productmold_history_complete,
         name='productmold_history_complete'),
    path('productmold_history/<int:pk>/delete/', views.productmold_history_delete, name='productmold_history_delete'),
    path('product_history/<int:pk>/delete/', views.product_history_delete, name='product_history_delete'),

]
