from django.urls import path
from donations import views

app_name = 'donations'

urlpatterns = [
    path('', views.donation_list_view, name='list'),
    path('create/', views.donation_create_view, name='create'),
    path('from-appointment/<int:appointment_pk>/', views.donation_create_from_appointment_view, name='create_from_appointment'),
    path('<int:pk>/', views.donation_detail_view, name='detail'),
]
