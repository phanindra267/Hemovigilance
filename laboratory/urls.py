from django.urls import path
from laboratory import views

app_name = 'laboratory'

urlpatterns = [
    path('bags/', views.blood_bag_list_view, name='blood_bag_list'),
    path('bags/<int:pk>/', views.blood_bag_detail_view, name='blood_bag_detail'),
    path('samples/', views.sample_list_view, name='sample_list'),
    path('samples/<int:pk>/', views.sample_detail_view, name='sample_detail'),
    path('samples/<int:sample_pk>/add-result/', views.add_screening_result_view, name='add_result'),
    path('samples/<int:pk>/verify/', views.verify_sample_view, name='verify_sample'),
]
