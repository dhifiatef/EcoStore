from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Products
    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Orders
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),

    # Messaging
    path('messages/', views.inbox, name='inbox'),
    path('messages/<int:store_id>/', views.conversation, name='conversation'),
    path('messages/<int:store_id>/contact/', views.contact_store, name='contact_store'),

    # AI
    path('ai-advisor/', views.ai_advisor, name='ai_advisor'),
    path('ai-advisor/chat/', views.ai_chat, name='ai_chat'),

    # Settings
    path('settings/', views.store_settings, name='store_settings'),
]
