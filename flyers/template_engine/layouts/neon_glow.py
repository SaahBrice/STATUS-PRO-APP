from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
from ...image_utils import remove_background, add_product_shadow
import textwrap

class NeonGlowLayout(TemplateComponent):
    """Modern neon-style layout with glowing effects"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        # Fonts
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 90)
            font_price = ImageFont.truetype("arialbd.ttf", 120)
            font_desc = ImageFont.truetype("arial.ttf", 36)
            font_cta = ImageFont.truetype("arialbd.ttf", 40)
        except:
            font_name = font_price = font_desc = font_cta = ImageFont.load_default()
        
        # === NEON CIRCLES BACKGROUND ===
        neon_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Draw glowing circles
        positions = [(200, 300), (width - 200, 200), (width - 300, height - 250)]
        
        for x, y in positions:
            # Multiple layers for glow effect
            for radius in range(150, 50, -20):
                opacity = int(30 * (150 - radius) / 100)
                overlay_draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                                   fill=neon_color + (opacity,))
        
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(image)
        
        # === PRODUCT IMAGE (Background Removed) ===
        # === LOAD PRODUCT IMAGE (Remove background if user chose to) ===
        try:
            if product.remove_background:
                product_img = remove_background(product.original_image.path)
            else:
                product_img = Image.open(product.original_image.path).convert('RGBA')

            product_img.thumbnail((int(width * 0.55), int(height * 0.50)), Image.LANCZOS)
            
            # Add dramatic shadow
            product_with_shadow = add_product_shadow(product_img, shadow_offset=40, shadow_blur=35)
            
            # Center product
            img_x = (width - product_with_shadow.width) // 2
            img_y = int(height * 0.20)
            
            image.paste(product_with_shadow, (img_x, img_y), product_with_shadow)
            
        except:
            product_img = Image.open(product.original_image.path).convert('RGBA')
            product_img.thumbnail((int(width * 0.45), int(height * 0.40)), Image.LANCZOS)
            img_x = (width - product_img.width) // 2
            img_y = int(height * 0.25)
            image.paste(product_img, (img_x, img_y), product_img)
        
        draw = ImageDraw.Draw(image)
        text_color = palette.get('text', '#FFFFFF')
        glow_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        
        # Calculate text area
        text_y = img_y + (product_img.height if 'product_with_shadow' not in locals() else product_with_shadow.height) + 60
        
        # === PRODUCT NAME (Glowing Text) ===
        name = (product.name or "Product").upper()
        name_lines = textwrap.wrap(name, width=20)
        
        for line in name_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=font_name)
            text_width = bbox[2] - bbox[0]
            text_x = (width - text_width) // 2
            
            # Glow layers
            for blur_level in [15, 10, 5]:
                for offset in range(-blur_level, blur_level + 1, 5):
                    draw.text((text_x + offset, text_y + offset), line, 
                             fill=glow_color, font=font_name)
            
            # Main text
            draw.text((text_x, text_y), line, fill=text_color, font=font_name)
            text_y += 100
        
        text_y += 40
        
        # === PRICE (Neon Box) ===
        price_text = f"{int(product.price or 0):,} FCFA"
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 80
        price_height = 160
        
        price_x = (width - price_width) // 2
        price_y = text_y
        
        # Neon border effect
        for thickness in [20, 15, 10, 5]:
            opacity = int(150 * (20 - thickness) / 20)
            draw.rounded_rectangle(
                [price_x - thickness, price_y - thickness, 
                 price_x + price_width + thickness, price_y + price_height + thickness],
                radius=30,
                outline=glow_color + (opacity,),
                width=2
            )
        
        # Solid box
        draw.rounded_rectangle(
            [price_x, price_y, price_x + price_width, price_y + price_height],
            radius=25,
            fill=glow_color
        )
        
        # Price text
        draw.text((price_x + 40, price_y + 25), price_text, fill='#FFFFFF', font=font_price)
        
        # === BOTTOM INFO ===
        bottom_y = height - 150
        
        info = []
        if product.contact_info:
            info.append(product.contact_info)
        if product.delivery_info:
            info.append(product.delivery_info)
        
        info_text = " | ".join(info)
        if info_text:
            bbox = draw.textbbox((0, 0), info_text, font=font_desc)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, bottom_y), info_text, 
                     fill=text_color, font=font_desc)
        
        return image.convert('RGB')
