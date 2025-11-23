from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
import textwrap

class CenteredLayout(TemplateComponent):
    """Professional centered layout with hero product image"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            font_brand = ImageFont.truetype("arialbd.ttf", 45)
            font_name = ImageFont.truetype("arialbd.ttf", 80)
            font_price = ImageFont.truetype("arialbd.ttf", 90)
            font_desc = ImageFont.truetype("arial.ttf", 35)
            font_info = ImageFont.truetype("arial.ttf", 30)
            font_cta = ImageFont.truetype("arialbd.ttf", 40)
        except:
            font_brand = font_name = font_price = font_desc = font_info = font_cta = ImageFont.load_default()
        
        # Load and process product image
        product_img = Image.open(product.original_image.path).convert('RGBA')
        
        # Make product image LARGE (70% of canvas width)
        img_max_width = int(width * 0.75)
        img_max_height = int(height * 0.50)
        product_img.thumbnail((img_max_width, img_max_height), Image.LANCZOS)
        
        # Add subtle shadow to product
        shadow = product_img.copy()
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        
        # Center product at top third
        img_x = (width - product_img.width) // 2
        img_y = int(height * 0.08)
        
        # Paste shadow first
        shadow_offset = 10
        if shadow.mode == 'RGBA':
            image.paste(shadow, (img_x + shadow_offset, img_y + shadow_offset), shadow)
        
        # Paste product image
        if product_img.mode == 'RGBA':
            image.paste(product_img, (img_x, img_y), product_img)
        else:
            image.paste(product_img, (img_x, img_y))
        
        # Calculate text start position
        text_start_y = img_y + product_img.height + 60
        
        # === PRODUCT NAME ===
        name = (product.name or "Product").upper()
        name_color = palette.get('text', '#FFFFFF')
        
        # Wrap text if too long
        if len(name) > 20:
            name_lines = textwrap.wrap(name, width=20)
            for i, line in enumerate(name_lines[:2]):  # Max 2 lines
                bbox = draw.textbbox((0, 0), line, font=font_name)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, text_start_y + i * 85), 
                         line, fill=name_color, font=font_name)
            text_start_y += 85 * min(len(name_lines), 2) + 20
        else:
            bbox = draw.textbbox((0, 0), name, font=font_name)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, text_start_y), 
                     name, fill=name_color, font=font_name)
            text_start_y += 100
        
        # === PRICE WITH BADGE ===
        price_text = f"{int(product.price or 0):,} FCFA"
        price_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        # Draw price badge background
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 60
        price_height = bbox[3] - bbox[1] + 40
        badge_x = (width - price_width) // 2
        badge_y = text_start_y
        
        # Rounded rectangle for price
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + price_width, badge_y + price_height],
            radius=20,
            fill=price_color
        )
        
        # Price text in contrasting color
        price_text_color = ColorGenerator.ensure_contrast('#FFFFFF', palette.get('secondary', '#FFD700'))
        draw.text((badge_x + 30, badge_y + 10), price_text, 
                 fill=price_text_color, font=font_price)
        
        text_start_y += price_height + 50
        
        # === DISCOUNT MESSAGE (if provided) ===
        if product.discount_message:
            discount_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
            discount_text = product.discount_message.upper()
            
            bbox = draw.textbbox((0, 0), discount_text, font=font_cta)
            disc_width = bbox[2] - bbox[0] + 50
            disc_height = bbox[3] - bbox[1] + 30
            disc_x = (width - disc_width) // 2
            disc_y = text_start_y
            
            # Draw discount badge
            draw.rounded_rectangle(
                [disc_x, disc_y, disc_x + disc_width, disc_y + disc_height],
                radius=15,
                fill=discount_bg
            )
            draw.text((disc_x + 25, disc_y + 10), discount_text, 
                     fill='#FFFFFF', font=font_cta)
            
            text_start_y += disc_height + 40
        
        # === DESCRIPTION ===
        if product.description:
            desc = product.description[:120] + "..." if len(product.description) > 120 else product.description
            desc_lines = textwrap.wrap(desc, width=40)
            
            for line in desc_lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=font_desc)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, text_start_y), 
                         line, fill=name_color, font=font_desc)
                text_start_y += 45
            
            text_start_y += 30
        
        # === BOTTOM INFO SECTION ===
        bottom_y = height - 220
        
        # Contact Info
        if product.contact_info:
            contact_text = f"📞 {product.contact_info}"
            bbox = draw.textbbox((0, 0), contact_text, font=font_info)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, bottom_y), 
                     contact_text, fill=name_color, font=font_info)
            bottom_y += 50
        
        # Delivery Info
        if product.delivery_info:
            delivery_text = f"🚚 {product.delivery_info}"
            bbox = draw.textbbox((0, 0), delivery_text, font=font_info)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, bottom_y), 
                     delivery_text, fill=name_color, font=font_info)
            bottom_y += 50
        
        # === CALL TO ACTION (Prominent) ===
        if product.call_to_action:
            cta_text = product.call_to_action.upper()
            cta_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
            
            bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
            cta_width = bbox[2] - bbox[0] + 60
            cta_height = bbox[3] - bbox[1] + 30
            cta_x = (width - cta_width) // 2
            cta_y = bottom_y + 10
            
            # Draw CTA button
            draw.rounded_rectangle(
                [cta_x, cta_y, cta_x + cta_width, cta_y + cta_height],
                radius=25,
                fill=cta_bg
            )
            draw.text((cta_x + 30, cta_y + 10), cta_text, 
                     fill='#FFFFFF', font=font_cta)
        
        return image
