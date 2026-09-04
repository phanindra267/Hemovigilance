from django.urls import path
from donors import views

app_name = 'donors'

urlpatterns = [
    path('', views.donor_list_view, name='list'),
    path('create/', views.donor_create_view, name='create'),
    path('<int:pk>/', views.donor_detail_view, name='detail'),
    path('<int:pk>/edit/', views.donor_update_view, name='update'),
    path('<int:donor_pk>/assessment/', views.eligibility_assessment_create_view, name='assess_eligibility'),
]
