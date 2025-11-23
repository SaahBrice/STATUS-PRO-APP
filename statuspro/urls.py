from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from flyers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('upload/', views.upload_view, name='upload'),
    path('product-details/', views.product_details_view, name='product_details'),
    path('product/<uuid:product_id>/edit/', views.product_detail_form_view, name='product_detail_form'),
    path('preview/', views.preview_designs, name='preview_designs'),
    
    # Download & Share
    path('download/<uuid:design_id>/', views.download_design, name='download_design'),
    path('download-selected/', views.download_selected, name='download_selected'),
    path('share/whatsapp/<uuid:design_id>/', views.share_to_whatsapp, name='share_whatsapp'),
    
    # API endpoints
    path('api/upload/', views.upload_image_ajax, name='upload_ajax'),
    path('api/bulk-upload/', views.bulk_upload_ajax, name='bulk_upload_ajax'),
    path('api/delete/<uuid:product_id>/', views.delete_image_ajax, name='delete_ajax'),
    path('api/product/<uuid:product_id>/save/', views.save_product_details_ajax, name='save_product_ajax'),
    path('api/design/<uuid:design_id>/toggle/', views.toggle_design_selection, name='toggle_design'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
