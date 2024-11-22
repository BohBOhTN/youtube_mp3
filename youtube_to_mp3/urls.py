from django.contrib import admin
from django.urls import path
from converter import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('process-link', views.process_link, name='process_link'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
