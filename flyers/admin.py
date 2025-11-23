from django.contrib import admin
from .models import Product, GeneratedDesign, UserSession

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'session_key', 'output_format', 'created_at']
    list_filter = ['output_format', 'created_at']
    search_fields = ['name', 'session_key']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(GeneratedDesign)
class GeneratedDesignAdmin(admin.ModelAdmin):
    list_display = ['product', 'template_name', 'is_selected', 'created_at']
    list_filter = ['is_selected', 'template_name', 'created_at']
    search_fields = ['product__name']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'products_count', 'created_at', 'last_activity']
    list_filter = ['created_at', 'last_activity']
    search_fields = ['session_key']
