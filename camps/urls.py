from django.urls import path
from camps import views

app_name = 'camps'

urlpatterns = [
    path('', views.camp_list_view, name='list'),
    path('create/', views.camp_create_view, name='create'),
    path('<int:pk>/', views.camp_detail_view, name='detail'),
    path('<int:pk>/register/', views.camp_register_donor_view, name='register_donor'),
]
