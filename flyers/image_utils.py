from PIL import Image, ImageOps
import os
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from rembg import remove
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np



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






def remove_background(image_field):
    """
    Remove background from product image using AI
    """
    img = Image.open(image_field)
    
    # Remove background
    output = remove(img)
    
    return output


def add_product_shadow(product_img, shadow_offset=30, shadow_blur=25, shadow_opacity=120):
    """
    Add realistic drop shadow to transparent product image
    """
    # Create shadow layer
    shadow = Image.new('RGBA', 
                      (product_img.width + shadow_offset * 2, 
                       product_img.height + shadow_offset * 2), 
                      (0, 0, 0, 0))
    
    # Create shadow shape
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse(
        [shadow_offset, shadow_offset, 
         product_img.width + shadow_offset, 
         product_img.height + shadow_offset],
        fill=(0, 0, 0, shadow_opacity)
    )
    
    # Blur shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # Composite product on shadow
    result = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
    result.paste(shadow, (0, 0), shadow)
    result.paste(product_img, (shadow_offset, shadow_offset), product_img)
    
    return result


def create_duotone_effect(image, color1, color2):
    """
    Create duotone effect on image
    """
    # Convert to grayscale
    gray = image.convert('L')
    
    # Create gradient from color1 to color2
    duotone = Image.new('RGB', gray.size)
    pixels = duotone.load()
    gray_pixels = gray.load()
    
    for y in range(gray.size[1]):
        for x in range(gray.size[0]):
            gray_value = gray_pixels[x, y] / 255.0
            
            r = int(color1[0] * (1 - gray_value) + color2[0] * gray_value)
            g = int(color1[1] * (1 - gray_value) + color2[1] * gray_value)
            b = int(color1[2] * (1 - gray_value) + color2[2] * gray_value)
            
            pixels[x, y] = (r, g, b)
    
    return duotone


def add_neon_glow(image, color, intensity=20):
    """
    Add neon glow effect around image edges
    """
    # Create glow layer
    glow = image.copy()
    
    # Apply multiple blur iterations for glow effect
    for i in range(intensity):
        glow = glow.filter(ImageFilter.GaussianBlur(5))
    
    # Tint with color
    enhancer = ImageEnhance.Color(glow)
    glow = enhancer.enhance(2.0)
    
    return glow
