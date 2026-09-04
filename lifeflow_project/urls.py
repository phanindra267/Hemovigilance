from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('donors/', include('donors.urls')),
    path('appointments/', include('appointments.urls')),
    path('camps/', include('camps.urls')),
    path('donations/', include('donations.urls')),
    path('laboratory/', include('laboratory.urls')),
    path('components/', include('blood_components.urls')),
    path('inventory/', include('inventory.urls')),
    path('requests/', include('requests_app.urls')),
    path('patients/', include('patients.urls')),
    path('hospitals/', include('hospitals.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('audit/', include('audit.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler400 = 'core.views.handler400'
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
