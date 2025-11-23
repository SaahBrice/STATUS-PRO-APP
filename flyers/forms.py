from django import forms
from .models import Product
from PIL import Image
import os


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images"""
    
    class Meta:
        model = Product
        fields = ['original_image']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/jpeg,image/png,image/jpg,image/webp',
                'multiple': False,
                'id': 'image-upload-input'
            })
        }
    
    def clean_original_image(self):
        image = self.cleaned_data.get('original_image')
        
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Image file too large. Maximum size is 10MB.')
            
            # Check file extension
            ext = os.path.splitext(image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            if ext not in valid_extensions:
                raise forms.ValidationError('Invalid file type. Please upload JPG, PNG, or WEBP images only.')
            
            # Validate image using PIL
            try:
                img = Image.open(image)
                img.verify()
                
                # Check minimum dimensions (at least 500x500)
                if img.width < 500 or img.height < 500:
                    raise forms.ValidationError('Image too small. Minimum size is 500x500 pixels.')
                
            except Exception:
                raise forms.ValidationError('Invalid or corrupted image file.')
        
        return image


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget that allows selecting multiple files."""
    allow_multiple_selected = True


class BulkUploadForm(forms.Form):
    """Form for bulk image uploads"""
    images = forms.FileField(
        widget=MultipleFileInput(attrs={
            'class': 'hidden',
            'accept': 'image/jpeg,image/png,image/jpg,image/webp',
            'multiple': True,
            'id': 'bulk-upload-input'
        }),
        required=False
    )
