from PIL import Image, ImageDraw, ImageFont
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
import textwrap

class DynamicDiagonalLayout(TemplateComponent):
    """Dynamic layout with diagonal elements and energy"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # === DIAGONAL ACCENT SHAPES ===
        color1 = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        color2 = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        
        # Top-left to bottom-right diagonal stripe
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Diagonal stripe
        points = [
            (0, 0),
            (int(width * 0.6), 0),
            (int(width * 0.4), height),
            (0, height)
        ]
        overlay_draw.polygon(points, fill=color1 + (30,))
        
        # Second diagonal
        points2 = [
            (int(width * 0.7), 0),
            (width, 0),
            (width, height),
            (int(width * 0.5), height)
        ]
        overlay_draw.polygon(points2, fill=color2 + (20,))
        
        image = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(image)
        
        # Fonts
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 90)
            font_price = ImageFont.truetype("arialbd.ttf", 95)
            font_desc = ImageFont.truetype("arial.ttf", 36)
            font_info = ImageFont.truetype("arial.ttf", 30)
            font_cta = ImageFont.truetype("arialbd.ttf", 42)
        except:
            font_name = font_price = font_desc = font_info = font_cta = ImageFont.load_default()
        
        text_color = palette.get('text', '#FFFFFF')
        
        # === PRODUCT NAME (Top, Angled) ===
        name = (product.name or "Product").upper()
        name_lines = textwrap.wrap(name, width=16)
        
        name_y = 70
        for line in name_lines[:2]:
            # Draw with outline for visibility
            for offset_x in range(-3, 4):
                for offset_y in range(-3, 4):
                    draw.text((80 + offset_x, name_y + offset_y), line, fill='#000000', font=font_name)
            
            draw.text((80, name_y), line, fill=text_color, font=font_name)
            name_y += 100
        
        # === PRODUCT IMAGE (Center-Left) ===
        product_img = Image.open(product.original_image.path).convert('RGBA')
        
        img_max_width = int(width * 0.50)
        img_max_height = int(height * 0.55)
        product_img.thumbnail((img_max_width, img_max_height), Image.LANCZOS)
        
        img_x = 80
        img_y = name_y + 40
        
        image.paste(product_img, (img_x, img_y), product_img)
        
        # === PRICE (Right Side, Vertical) ===
        price_text = f"{int(product.price or 0):,}"
        price_bg = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        price_x = int(width * 0.60)
        price_y = int(height * 0.35)
        
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 60
        price_height = 140
        
        # Rotated price badge
        draw.rounded_rectangle(
            [price_x, price_y, price_x + price_width, price_y + price_height],
            radius=20,
            fill=price_bg
        )
        
        draw.text((price_x + 30, price_y + 20), price_text, fill='#000000', font=font_price)
        draw.text((price_x + 30, price_y + 105), "FCFA", fill='#000000', font=ImageFont.truetype("arialbd.ttf", 35) if True else font_info)
        
        # === INFO SECTION (Bottom Right) ===
        info_x = int(width * 0.55)
        info_y = int(height * 0.60)
        
        if product.discount_message:
            disc_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
            disc_text = product.discount_message.upper()
            
            bbox = draw.textbbox((0, 0), disc_text, font=font_cta)
            disc_width = bbox[2] - bbox[0] + 50
            disc_height = 70
            
            draw.rounded_rectangle(
                [info_x, info_y, info_x + disc_width, info_y + disc_height],
                radius=15,
                fill=disc_bg
            )
            draw.text((info_x + 25, info_y + 15), disc_text, fill='#FFFFFF', font=font_cta)
            
            info_y += disc_height + 30
        
        # Description
        if product.description:
            desc = product.description[:80] + "..." if len(product.description) > 80 else product.description
            desc_lines = textwrap.wrap(desc, width=22)
            
            for line in desc_lines[:2]:
                draw.text((info_x, info_y), line, fill=text_color, font=font_desc)
                info_y += 45
            
            info_y += 20
        
        # Contact/Delivery
        if product.contact_info:
            contact_lines = textwrap.wrap(f"📞 {product.contact_info}", width=20)
            for line in contact_lines[:1]:
                draw.text((info_x, info_y), line, fill=text_color, font=font_info)
                info_y += 40
        
        if product.delivery_info:
            delivery_lines = textwrap.wrap(f"🚚 {product.delivery_info}", width=20)
            for line in delivery_lines[:1]:
                draw.text((info_x, info_y), line, fill=text_color, font=font_info)
        
        # CTA (Bottom)
        if product.call_to_action:
            cta_text = product.call_to_action.upper()
            cta_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
            
            cta_y = height - 150
            bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
            cta_width = bbox[2] - bbox[0] + 60
            
            draw.rounded_rectangle(
                [80, cta_y, 80 + cta_width, cta_y + 75],
                radius=25,
                fill=cta_bg
            )
            draw.text((110, cta_y + 15), cta_text, fill='#FFFFFF', font=font_cta)
        
        return image
