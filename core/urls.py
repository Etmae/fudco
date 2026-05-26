from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),  # all our routes live in store/urls.py
]

# This ensures that both locally (DEBUG=True) and on Render (DEBUG=False), 
# Django will route media requests correctly.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)