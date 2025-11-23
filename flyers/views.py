from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Product, UserSession
from .forms import ProductImageForm, BulkUploadForm
from .session_utils import get_or_create_session, get_session_products
from .image_utils import create_thumbnail, optimize_image, generate_safe_filename
import json

def home(request):
    """Landing page view"""
    user_session = get_or_create_session(request)
    
    context = {
        'session_key': request.session.session_key
    }
    
    return render(request, 'home.html', context)


def upload_view(request):
    """Upload interface view"""
    user_session = get_or_create_session(request)
    form = ProductImageForm()
    bulk_form = BulkUploadForm()
    
    # Get existing uploads for this session
    products = get_session_products(request)
    
    context = {
        'form': form,
        'bulk_form': bulk_form,
        'products': products,
        'session_key': request.session.session_key
    }
    
    return render(request, 'upload.html', context)


@require_http_methods(["POST"])
def upload_image_ajax(request):
    """Handle AJAX image upload"""
    if request.FILES.get('original_image'):
        form = ProductImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Get or create session
            user_session = get_or_create_session(request)
            
            # Create product instance
            product = form.save(commit=False)
            product.session_key = request.session.session_key
            
            # Optimize and save image with safe filename
            optimized = optimize_image(product.original_image)
            safe_filename = generate_safe_filename(product.original_image.name)
            product.original_image.save(
                safe_filename,
                optimized,
                save=False
            )
            
            # Generate thumbnail
            thumbnail = create_thumbnail(product.original_image)
            thumbnail_name = f"thumb_{safe_filename}"
            product.thumbnail.save(thumbnail_name, thumbnail, save=False)
            
            product.save()
            
            # Update session product count
            user_session.products_count += 1
            user_session.save()
            
            return JsonResponse({
                'success': True,
                'product_id': str(product.id),
                'thumbnail_url': product.thumbnail.url,
                'message': 'Image uploaded successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'No image file provided'
    }, status=400)


@require_http_methods(["POST"])
def bulk_upload_ajax(request):
    """Handle bulk image uploads"""
    uploaded_products = []
    errors = []
    
    user_session = get_or_create_session(request)
    
    files = request.FILES.getlist('images')
    
    if not files:
        return JsonResponse({
            'success': False,
            'message': 'No files provided'
        }, status=400)
    
    for file in files:
        try:
            # Create form for each file
            form = ProductImageForm(files={'original_image': file})
            
            if form.is_valid():
                product = form.save(commit=False)
                product.session_key = request.session.session_key
                
                # Optimize image with safe filename
                optimized = optimize_image(product.original_image)
                safe_filename = generate_safe_filename(product.original_image.name)
                product.original_image.save(
                    safe_filename,
                    optimized,
                    save=False
                )
                
                # Generate thumbnail
                thumbnail = create_thumbnail(product.original_image)
                thumbnail_name = f"thumb_{safe_filename}"
                product.thumbnail.save(thumbnail_name, thumbnail, save=False)
                
                product.save()
                
                uploaded_products.append({
                    'id': str(product.id),
                    'thumbnail': product.thumbnail.url,
                    'name': file.name
                })
                
                user_session.products_count += 1
            else:
                errors.append({
                    'file': file.name,
                    'errors': form.errors.as_json()
                })
        except Exception as e:
            errors.append({
                'file': file.name,
                'error': str(e)
            })
    
    user_session.save()
    
    return JsonResponse({
        'success': True,
        'uploaded': len(uploaded_products),
        'products': uploaded_products,
        'errors': errors
    })


@require_http_methods(["DELETE"])
def delete_image_ajax(request, product_id):
    """Delete uploaded image"""
    try:
        product = Product.objects.get(
            id=product_id,
            session_key=request.session.session_key
        )
        
        # Delete the product (images will be deleted automatically)
        product.delete()
        
        # Update session count
        user_session = UserSession.objects.get(session_key=request.session.session_key)
        user_session.products_count = max(0, user_session.products_count - 1)
        user_session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Image deleted successfully'
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Image not found'
        }, status=404)
