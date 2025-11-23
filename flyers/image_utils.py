from PIL import Image, ImageOps
import os
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def generate_safe_filename(original_filename):
    """Generate a short, safe filename"""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex[:12]}{ext}"

def create_thumbnail(image_field, size=(300, 300)):
    """
    Create a thumbnail from uploaded image
    """
    img = Image.open(image_field)
    
    # Convert to RGB if necessary
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Create thumbnail maintaining aspect ratio
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Save to BytesIO
    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG', quality=85, optimize=True)
    thumb_io.seek(0)
    
    return ContentFile(thumb_io.read())


def optimize_image(image_field, max_size=(2048, 2048)):
    """
    Optimize uploaded image for storage
    """
    img = Image.open(image_field)
    
    # Apply EXIF orientation
    img = ImageOps.exif_transpose(img)
    
    # Convert to RGB
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Resize if too large
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save optimized
    output = BytesIO()
    img.save(output, format='JPEG', quality=90, optimize=True)
    output.seek(0)
    
    return ContentFile(output.read())


def validate_image_format(image_file):
    """
    Validate image format and integrity
    """
    try:
        img = Image.open(image_file)
        img.verify()
        return True, None
    except Exception as e:
        return False, str(e)
