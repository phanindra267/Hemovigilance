from django.urls import path
from audit import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_log_list_view, name='list'),
    path('<int:pk>/', views.audit_log_detail_view, name='detail'),
]
