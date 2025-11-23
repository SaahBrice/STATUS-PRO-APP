from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
from ...image_utils import remove_background, add_product_shadow
import textwrap

class MagazineStyleLayout(TemplateComponent):
    """Magazine-style layout with background-removed product overlapping text"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Fonts
        try:
            font_huge = ImageFont.truetype("arialbd.ttf", 180)
            font_name = ImageFont.truetype("arialbd.ttf", 95)
            font_price = ImageFont.truetype("arialbd.ttf", 110)
            font_desc = ImageFont.truetype("arial.ttf", 38)
            font_info = ImageFont.truetype("arialbd.ttf", 35)
        except:
            font_huge = font_name = font_price = font_desc = font_info = ImageFont.load_default()
        
        # === HUGE BACKGROUND TEXT ===
        text_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        bg_text = (product.name or "PRODUCT").upper()[:8]
        
        # Draw huge semi-transparent text as background
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Diagonal background text
        for i, char in enumerate(bg_text):
            y_pos = 100 + i * 200
            overlay_draw.text((50, y_pos), char, fill=text_color + (30,), font=font_huge)
        
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(image)
        
        # === REMOVE BACKGROUND FROM PRODUCT ===
        # === LOAD PRODUCT IMAGE (Remove background if user chose to) ===
        try:
            if product.remove_background:
                product_img = remove_background(product.original_image.path)
            else:
                product_img = Image.open(product.original_image.path).convert('RGBA')

            
            # Resize product (large)
            product_img.thumbnail((int(width * 0.65), int(height * 0.60)), Image.LANCZOS)
            
            # Add shadow
            product_with_shadow = add_product_shadow(product_img)
            
            # Position product (offset to right, overlapping text)
            img_x = int(width * 0.30)
            img_y = int(height * 0.25)
            
            # Paste product
            image.paste(product_with_shadow, (img_x, img_y), product_with_shadow)
            
        except Exception as e:
            print(f"Background removal failed: {e}")
            # Fallback: use original image
            product_img = Image.open(product.original_image.path).convert('RGBA')
            product_img.thumbnail((int(width * 0.50), int(height * 0.45)), Image.LANCZOS)
            img_x = int(width * 0.35)
            img_y = int(height * 0.30)
            image.paste(product_img, (img_x, img_y), product_img)
        
        draw = ImageDraw.Draw(image)
        text_color_solid = palette.get('text', '#FFFFFF')
        
        # === TOP: PRODUCT NAME ===
        name = (product.name or "Product").upper()
        name_lines = textwrap.wrap(name, width=18)
        
        y_pos = 80
        for line in name_lines[:2]:
            # Outlined text for visibility
            for offset in range(-4, 5):
                for offset_y in range(-4, 5):
                    draw.text((80 + offset, y_pos + offset_y), line, fill='#000000', font=font_name)
            
            draw.text((80, y_pos), line, fill=text_color_solid, font=font_name)
            y_pos += 110
        
        # === PRICE (Bottom Left, Bold Badge) ===
        price_text = f"{int(product.price or 0):,}"
        price_bg = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        price_x = 80
        price_y = height - 350
        
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 70
        price_height = 150
        
        # Skewed rectangle effect (draw as polygon)
        points = [
            (price_x, price_y),
            (price_x + price_width - 20, price_y),
            (price_x + price_width, price_y + price_height),
            (price_x + 20, price_y + price_height)
        ]
        
        # Shadow
        shadow_points = [(x + 8, y + 8) for x, y in points]
        draw.polygon(shadow_points, fill=(0, 0, 0, 100))
        
        # Main shape
        draw.polygon(points, fill=price_bg)
        
        # Price text
        draw.text((price_x + 35, price_y + 15), price_text, fill='#000000', font=font_price)
        draw.text((price_x + 35, price_y + 110), "FCFA", fill='#000000', font=ImageFont.truetype("arialbd.ttf", 40) if True else font_info)
        
        # === DISCOUNT BADGE (Top Right) ===
        if product.discount_message:
            disc_text = product.discount_message.upper()
            disc_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
            
            disc_x = width - 250
            disc_y = 80
            
            # Circular badge
            draw.ellipse([disc_x, disc_y, disc_x + 200, disc_y + 200], fill=disc_color)
            
            # Inner circle
            inner_color = tuple(min(c + 50, 255) for c in disc_color)
            draw.ellipse([disc_x + 25, disc_y + 25, disc_x + 175, disc_y + 175], fill=inner_color)
            
            # Text
            bbox = draw.textbbox((0, 0), disc_text, font=font_info)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            draw.text((disc_x + (200 - text_w) // 2, disc_y + (200 - text_h) // 2 - 10), 
                     disc_text, fill='#FFFFFF', font=font_info)
        
        # === INFO BAR (Bottom) ===
        info_y = height - 180
        
        info_items = []
        if product.contact_info:
            info_items.append(f"📞 {product.contact_info}")
        if product.delivery_info:
            info_items.append(f"🚚 {product.delivery_info}")
        
        info_text = " • ".join(info_items)
        if info_text:
            draw.text((80, info_y), info_text, fill=text_color_solid, font=font_desc)
        
        # === CTA (Bottom Right) ===
        if product.call_to_action:
            cta_text = product.call_to_action.upper()
            cta_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
            
            bbox = draw.textbbox((0, 0), cta_text, font=font_info)
            cta_width = bbox[2] - bbox[0] + 60
            
            cta_x = width - cta_width - 80
            cta_y = height - 120
            
            draw.rounded_rectangle(
                [cta_x, cta_y, cta_x + cta_width, cta_y + 75],
                radius=20,
                fill=cta_bg
            )
            draw.text((cta_x + 30, cta_y + 18), cta_text, fill='#FFFFFF', font=font_info)
        
        return image.convert('RGB')
