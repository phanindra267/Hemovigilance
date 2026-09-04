from django.urls import path
from inventory import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_stock_view, name='stock'),
    path('<int:pk>/', views.inventory_detail_view, name='detail'),
    path('<int:pk>/quarantine/', views.quarantine_item_view, name='quarantine'),
    path('<int:pk>/release/', views.release_quarantine_view, name='release'),
    path('temperature/', views.temperature_log_list_view, name='temperature_list'),
    path('temperature/add/', views.temperature_log_create_view, name='temperature_add'),
]
