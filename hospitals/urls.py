from django.urls import path
from hospitals import views

app_name = 'hospitals'

urlpatterns = [
    path('', views.hospital_list_view, name='list'),
    path('create/', views.hospital_create_view, name='create'),
    path('<int:pk>/', views.hospital_detail_view, name='detail'),
    path('<int:pk>/edit/', views.hospital_update_view, name='update'),
]
