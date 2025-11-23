from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Product, UserSession
from .forms import ProductImageForm, BulkUploadForm, ProductDetailsForm
from .session_utils import get_or_create_session, get_session_products
from .image_utils import create_thumbnail, optimize_image, generate_safe_filename
import json
from django.http import HttpResponse, FileResponse
from zipfile import ZipFile
from django.contrib import messages
import mimetypes
from .models import Product, UserSession, GeneratedDesign
from .template_engine.template_generator import TemplateGenerator
from django.core.files.base import ContentFile
from io import BytesIO







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


def product_details_view(request):
    """View to add details for uploaded products"""
    user_session = get_or_create_session(request)
    products = get_session_products(request)
    
    # Filter products without complete information
    incomplete_products = products.filter(name='') | products.filter(price__isnull=True)
    
    context = {
        'products': incomplete_products,
        'total_products': products.count(),
        'session_key': request.session.session_key
    }
    
    return render(request, 'product_details.html', context)


def product_detail_form_view(request, product_id):
    """View to edit a specific product's details"""
    try:
        product = Product.objects.get(
            id=product_id,
            session_key=request.session.session_key
        )
    except Product.DoesNotExist:
        return redirect('upload')
    
    if request.method == 'POST':
        form = ProductDetailsForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            
            # Check if there are more products to fill
            remaining = get_session_products(request).filter(
                name=''
            ).exclude(id=product_id).first()
            
            if remaining:
                return redirect('product_detail_form', product_id=remaining.id)
            else:
                return redirect('preview_designs')
        else:
            context = {
                'form': form,
                'product': product,
                'errors': form.errors
            }
            return render(request, 'product_form.html', context)
    else:
        form = ProductDetailsForm(instance=product)
        
        context = {
            'form': form,
            'product': product
        }
        
        return render(request, 'product_form.html', context)


@require_http_methods(["POST"])
def save_product_details_ajax(request, product_id):
    """Handle AJAX product details save"""
    try:
        product = Product.objects.get(
            id=product_id,
            session_key=request.session.session_key
        )
        
        form = ProductDetailsForm(request.POST, instance=product)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Product details saved!'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def preview_designs(request):
    """Placeholder for preview page"""
    products = get_session_products(request)
    context = {
        'products': products
    }
    return render(request, 'preview.html', context)


def generate_designs_for_product(product):
    """Generate template designs for a product using all layouts"""
    generator = TemplateGenerator()
    
    # Get number of layouts available
    layout_count = generator.get_layout_count()
    
    # Generate 1 template per layout (total: 5 templates)
    # Or use templates_per_layout=2 for 10 templates, etc.
    templates = generator.generate_templates(product, templates_per_layout=1)
    
    # Save each template as GeneratedDesign
    for idx, template_img in enumerate(templates):
        # Save image to BytesIO
        img_io = BytesIO()
        template_img.save(img_io, format='JPEG', quality=95)
        img_io.seek(0)
        
        # Get layout name for better tracking
        layout_names = ['centered', 'split', 'hero', 'minimal', 'diagonal']
        layout_name = layout_names[idx % len(layout_names)]
        
        # Create GeneratedDesign instance
        design = GeneratedDesign(
            product=product,
            template_name=f"{layout_name}_{idx + 1}"
        )
        
        # Save the design file
        filename = f"{product.id}_{layout_name}_{idx + 1}.jpg"
        design.design_file.save(filename, ContentFile(img_io.read()), save=False)
        design.save()
    
    return True



def preview_designs(request):
    """Preview generated designs"""
    products = get_session_products(request)
    
    # Generate designs for products that don't have them
    for product in products:
        if product.designs.count() == 0:
            try:
                generate_designs_for_product(product)
            except Exception as e:
                print(f"Error generating designs for {product.id}: {e}")
    
    # Reload products with designs
    products = get_session_products(request).prefetch_related('designs')
    
    context = {
        'products': products
    }
    return render(request, 'preview.html', context)


@require_http_methods(["POST"])
def toggle_design_selection(request, design_id):
    """Toggle design selection"""
    try:
        import json
        data = json.loads(request.body)
        
        design = GeneratedDesign.objects.get(
            id=design_id,
            product__session_key=request.session.session_key
        )
        
        design.is_selected = data.get('selected', False)
        design.save()
        
        return JsonResponse({
            'success': True,
            'selected': design.is_selected
        })
    except GeneratedDesign.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Design not found'
        }, status=404)






def download_design(request, design_id):
    """Download a single design"""
    try:
        design = GeneratedDesign.objects.get(
            id=design_id,
            product__session_key=request.session.session_key
        )
        
        # Open the file
        file_path = design.design_file.path
        filename = f"{design.product.name}_{design.template_name}.jpg"
        
        # Serve the file
        response = FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Track download
        design.times_selected += 1
        design.save()
        
        return response
        
    except GeneratedDesign.DoesNotExist:
        return HttpResponse("Design not found", status=404)


def download_selected(request):
    """Download all selected designs as a ZIP file"""
    # Get all selected designs for this session
    selected_designs = GeneratedDesign.objects.filter(
        product__session_key=request.session.session_key,
        is_selected=True
    )
    
    if not selected_designs.exists():
        messages.warning(request, 'No designs selected. Please select at least one design.')
        return redirect('preview_designs')
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    
    with ZipFile(zip_buffer, 'w') as zip_file:
        for design in selected_designs:
            # Read the design file
            with open(design.design_file.path, 'rb') as f:
                file_data = f.read()
            
            # Add to ZIP with descriptive name
            filename = f"{design.product.name}_{design.template_name}.jpg"
            zip_file.writestr(filename, file_data)
    
    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="status_pro_flyers.zip"'
    
    return response


def share_to_whatsapp(request, design_id):
    """Prepare design for WhatsApp sharing"""
    try:
        design = GeneratedDesign.objects.get(
            id=design_id,
            product__session_key=request.session.session_key
        )
        
        context = {
            'design': design,
            'design_url': request.build_absolute_uri(design.design_file.url)
        }
        
        return render(request, 'share_whatsapp.html', context)
        
    except GeneratedDesign.DoesNotExist:
        return HttpResponse("Design not found", status=404)

