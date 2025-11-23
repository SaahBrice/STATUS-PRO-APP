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


class ProductDetailsForm(forms.ModelForm):
    """Form for adding product details"""
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'discount_message', 'contact_info', 
                  'delivery_info', 'call_to_action', 'output_format', 'remove_background']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-cyan-500 focus:outline-none transition-all',
                'placeholder': 'e.g., iPhone 13 Pro Max',
                'maxlength': '200',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-cyan-500 focus:outline-none transition-all',
                'placeholder': 'e.g., 450000',
                'min': '0',
                'step': '1',
                'required': True,
                'inputmode': 'numeric'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-cyan-500 focus:outline-none transition-all',
                'placeholder': 'Brief description to attract customers...',
                'rows': '3',
                'maxlength': '500'
            }),
            'discount_message': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-purple-500 focus:outline-none transition-all',
                'placeholder': 'e.g., 20% OFF Today Only!',
                'maxlength': '100'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-purple-500 focus:outline-none transition-all',
                'placeholder': 'e.g., WhatsApp: +237 6XX XXX XXX',
                'maxlength': '100'
            }),
            'delivery_info': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-purple-500 focus:outline-none transition-all',
                'placeholder': 'e.g., Free delivery in Douala',
                'maxlength': '200'
            }),
            'call_to_action': forms.TextInput(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-purple-500 focus:outline-none transition-all',
                'placeholder': 'e.g., Order Now!',
                'maxlength': '100'
            }),
            'output_format': forms.Select(attrs={
                'class': 'w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-cyan-500 focus:outline-none transition-all'
            }),
            'remove_background': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-cyan-600 bg-gray-800 border-gray-700 rounded focus:ring-cyan-500'
            })
        }
        labels = {
            'name': 'Product Name *',
            'price': 'Price (CFA Francs) *',
            'description': 'Description',
            'discount_message': 'Special Offer/Discount',
            'contact_info': 'Contact Information',
            'delivery_info': 'Delivery Details',
            'call_to_action': 'Call to Action',
            'output_format': 'Flyer Format *',
            'remove_background': 'Remove Image Background (Recommended for better effects)'
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative')
        return price
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 2:
            raise forms.ValidationError('Product name must be at least 2 characters')
        return name.strip() if name else name


