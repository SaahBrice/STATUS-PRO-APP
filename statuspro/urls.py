from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from flyers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('upload/', views.upload_view, name='upload'),
    path('api/upload/', views.upload_image_ajax, name='upload_ajax'),
    path('api/bulk-upload/', views.bulk_upload_ajax, name='bulk_upload_ajax'),
    path('api/delete/<uuid:product_id>/', views.delete_image_ajax, name='delete_ajax'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
