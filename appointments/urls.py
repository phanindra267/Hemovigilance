from django.urls import path
from appointments import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list_view, name='list'),
    path('create/', views.appointment_create_view, name='create'),
    path('<int:pk>/checkin/', views.appointment_checkin_view, name='checkin'),
    path('<int:pk>/cancel/', views.appointment_cancel_view, name='cancel'),
]
