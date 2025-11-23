from django.db import models
from django.utils import timezone
import uuid

class Product(models.Model):
    """Stores product information and uploaded image"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_key = models.CharField(max_length=40, db_index=True)
    
    # Product details - make them optional for now
    name = models.CharField(max_length=200, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True, default=0)
    description = models.TextField(blank=True, default='')
    discount_message = models.CharField(max_length=100, blank=True, default='')
    contact_info = models.CharField(max_length=100, blank=True, default='')
    delivery_info = models.CharField(max_length=200, blank=True, default='')
    call_to_action = models.CharField(max_length=100, blank=True, default='')
    
    # Image
    original_image = models.ImageField(upload_to='uploads/%Y/%m/%d/', max_length=500)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True, max_length=500)
    remove_background = models.BooleanField(
        default=False,
        help_text="Remove background from product image for better design effects"
    )
    # Format selection
    FORMAT_CHOICES = [
        ('square', 'Square (1080x1080) - Instagram'),
        ('portrait', 'Portrait (1080x1920) - Stories'),
        ('landscape', 'Landscape (1920x1080) - General'),
    ]
    output_format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='square')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_key', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name or 'Unnamed Product'} - {self.price or 0} CFA"



class GeneratedDesign(models.Model):
    """Stores generated flyer designs for each product"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='designs')
    
    # Design details
    template_name = models.CharField(max_length=50)
    design_file = models.ImageField(upload_to='designs/%Y/%m/%d/')
    
    # Selection tracking
    is_selected = models.BooleanField(default=False)
    times_selected = models.IntegerField(default=0) 

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['template_name']
    
    def __str__(self):
        return f"{self.product.name} - {self.template_name}"


class UserSession(models.Model):
    """Tracks session metadata for cleanup and analytics"""
    session_key = models.CharField(max_length=40, unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    products_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Session {self.session_key[:8]}... ({self.products_count} products)"
