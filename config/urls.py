"""
URL configuration for EnvPlus project.
...
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- NEW
from django.conf.urls.static import static # <-- NEW


urlpatterns = [
    # 1. Django Admin Panel
    path('admin/', admin.site.urls),

    # 2. Newsfeed Application URLs (Frontend & APIs)
    path('news/', include('newsfeed.urls')),

    # 3. Django REST Framework authentication URLs
    path('api-auth/', include('rest_framework.urls')),
]

# =========================================================
# DEVELOPMENT SETTINGS: SERVE STATIC & MEDIA FILES <-- NEW
# Ye code sirf DEBUG=True hone par files serve karta hai.
# =========================================================
if settings.DEBUG:
    # Serve static files (CSS, JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Serve media files (Uploaded Images)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)