from django.urls import path
from reports import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index_view, name='index'),
    path('donors/', views.donor_report_view, name='donors'),
    path('donations/', views.donation_report_view, name='donations'),
    path('inventory/', views.inventory_report_view, name='inventory'),
    path('issues/', views.issue_report_view, name='issues'),
    path('discards/', views.discard_report_view, name='discards'),
    path('rare-donors/', views.rare_donor_report_view, name='rare_donors'),
    path('monthly-summary/', views.monthly_summary_view, name='monthly_summary'),
]
