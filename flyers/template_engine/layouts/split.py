from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
import textwrap

class SplitLayout(TemplateComponent):
    """Professional split layout - Product left, info right"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 70)
            font_price = ImageFont.truetype("arialbd.ttf", 80)
            font_desc = ImageFont.truetype("arial.ttf", 32)
            font_info = ImageFont.truetype("arial.ttf", 28)
            font_cta = ImageFont.truetype("arialbd.ttf", 38)
            font_discount = ImageFont.truetype("arialbd.ttf", 35)
        except:
            font_name = font_price = font_desc = font_info = font_cta = font_discount = ImageFont.load_default()
        
        # === LEFT SIDE: PRODUCT IMAGE ===
        product_img = Image.open(product.original_image.path).convert('RGBA')
        
        # Product takes 50% of width, 90% of height
        img_max_width = int(width * 0.48)
        img_max_height = int(height * 0.90)
        product_img.thumbnail((img_max_width, img_max_height), Image.LANCZOS)
        
        # Center on left side
        img_x = (width // 2 - product_img.width) // 2
        img_y = (height - product_img.height) // 2
        
        # Paste product
        if product_img.mode == 'RGBA':
            image.paste(product_img, (img_x, img_y), product_img)
        else:
            image.paste(product_img, (img_x, img_y))
        
        # === RIGHT SIDE: TEXT CONTENT ===
        text_x = int(width * 0.53)
        text_y = int(height * 0.12)
        text_color = palette.get('text', '#FFFFFF')
        max_text_width = int(width * 0.42)
        
        # Product Name
        name = (product.name or "Product").upper()
        name_lines = textwrap.wrap(name, width=15)
        
        for line in name_lines[:2]:
            draw.text((text_x, text_y), line, fill=text_color, font=font_name)
            text_y += 80
        
        text_y += 30
        
        # Price Badge
        price_text = f"{int(product.price or 0):,}"
        price_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 40
        price_height = bbox[3] - bbox[1] + 30
        
        draw.rounded_rectangle(
            [text_x, text_y, text_x + price_width, text_y + price_height],
            radius=15,
            fill=price_color
        )
        draw.text((text_x + 20, text_y + 10), price_text, 
                 fill='#000000', font=font_price)
        
        # FCFA label
        draw.text((text_x, text_y + price_height + 5), "FCFA", 
                 fill=text_color, font=font_info)
        
        text_y += price_height + 70
        
        # Discount Message
        if product.discount_message:
            discount_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
            disc_text = f"🎁 {product.discount_message}"
            
            bbox = draw.textbbox((0, 0), disc_text, font=font_discount)
            disc_width = min(bbox[2] - bbox[0] + 40, max_text_width)
            disc_height = bbox[3] - bbox[1] + 25
            
            draw.rounded_rectangle(
                [text_x, text_y, text_x + disc_width, text_y + disc_height],
                radius=12,
                fill=discount_bg
            )
            draw.text((text_x + 20, text_y + 8), disc_text, 
                     fill='#FFFFFF', font=font_discount)
            
            text_y += disc_height + 50
        
        # Description
        if product.description:
            desc = product.description[:150] + "..." if len(product.description) > 150 else product.description
            desc_lines = textwrap.wrap(desc, width=25)
            
            for line in desc_lines[:4]:
                draw.text((text_x, text_y), line, fill=text_color, font=font_desc)
                text_y += 42
            
            text_y += 40
        
        # Contact & Delivery Info
        if product.contact_info:
            contact_lines = textwrap.wrap(f"📞 {product.contact_info}", width=25)
            for line in contact_lines[:2]:
                draw.text((text_x, text_y), line, fill=text_color, font=font_info)
                text_y += 38
            text_y += 20
        
        if product.delivery_info:
            delivery_lines = textwrap.wrap(f"🚚 {product.delivery_info}", width=25)
            for line in delivery_lines[:2]:
                draw.text((text_x, text_y), line, fill=text_color, font=font_info)
                text_y += 38
            text_y += 30
        
        # Call to Action
        if product.call_to_action:
            cta_text = product.call_to_action.upper()
            cta_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
            
            bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
            cta_width = min(bbox[2] - bbox[0] + 50, max_text_width)
            cta_height = bbox[3] - bbox[1] + 28
            
            draw.rounded_rectangle(
                [text_x, text_y, text_x + cta_width, text_y + cta_height],
                radius=20,
                fill=cta_bg
            )
            draw.text((text_x + 25, text_y + 10), cta_text, 
                     fill='#FFFFFF', font=font_cta)
        
        return image
