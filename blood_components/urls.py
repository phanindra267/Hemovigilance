from django.urls import path
from blood_components import views

app_name = 'blood_components'

urlpatterns = [
    path('', views.component_list_view, name='list'),
    path('<int:pk>/', views.component_detail_view, name='detail'),
    path('separate/<int:bag_pk>/', views.separate_components_view, name='separate'),
]
