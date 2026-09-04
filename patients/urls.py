from django.urls import path
from patients import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list_view, name='list'),
    path('create/', views.patient_create_view, name='create'),
    path('<int:pk>/', views.patient_detail_view, name='detail'),
    path('<int:pk>/edit/', views.patient_update_view, name='update'),
]
