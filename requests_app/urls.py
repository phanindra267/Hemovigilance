from django.urls import path
from requests_app import views

app_name = 'requests_app'

urlpatterns = [
    path('', views.request_list_view, name='list'),
    path('create/', views.request_create_view, name='create'),
    path('<int:pk>/', views.request_detail_view, name='detail'),
    path('<int:pk>/review/', views.request_review_view, name='review'),
    path('reserve/<int:item_pk>/', views.reserve_inventory_view, name='reserve_inventory'),
    path('reservation/<int:rsv_pk>/cancel/', views.cancel_reservation_view, name='cancel_reservation'),
    path('reservation/<int:rsv_pk>/issue/', views.issue_blood_view, name='issue_blood'),
    path('issue/<int:issue_pk>/return/', views.return_blood_view, name='return_blood'),
    path('inventory/<int:inv_pk>/discard/', views.discard_unit_view, name='discard_unit'),
]
