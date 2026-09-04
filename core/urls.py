from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('guidelines/', views.guidelines_view, name='guidelines'),
]
