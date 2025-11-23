from PIL import Image, ImageDraw, ImageFont
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator
import math

class DiscountBadge(TemplateComponent):
    """Attractive discount badge overlay"""
    
    def apply(self, image, context):
        if not context.get('product').discount_message:
            return image
        
        width, height = image.size
        palette = context.get('color_palette', {})
        
        # Create badge
        badge_size = 200
        badge = Image.new('RGBA', (badge_size, badge_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)
        
        # Draw star-burst badge
        color = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
        
        # Outer circle
        draw.ellipse([10, 10, badge_size-10, badge_size-10], fill=color + (255,))
        
        # Inner lighter circle
        inner_color = tuple(min(c + 40, 255) for c in color)
        draw.ellipse([30, 30, badge_size-30, badge_size-30], fill=inner_color + (255,))
        
        # Text
        try:
            font = ImageFont.truetype("arialbd.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        text = context.get('product').discount_message.upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(((badge_size - text_width) // 2, (badge_size - text_height) // 2 - 10), 
                 text, fill='#FFFFFF', font=font)
        
        # Position badge (top right corner)
        badge_x = width - badge_size - 30
        badge_y = 30
        
        # Paste on image
        image.paste(badge, (badge_x, badge_y), badge)
        
        return image


class PriceBadge(TemplateComponent):
    """Prominent price tag overlay"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Price badge background
        badge_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        price_text = f"{int(product.price or 0):,}"
        
        try:
            font_price = ImageFont.truetype("arialbd.ttf", 90)
            font_currency = ImageFont.truetype("arialbd.ttf", 40)
        except:
            font_price = font_currency = ImageFont.load_default()
        
        # Calculate badge size
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        badge_width = bbox[2] - bbox[0] + 80
        badge_height = 140
        
        # Position (bottom center or as specified)
        badge_x = (width - badge_width) // 2
        badge_y = height - badge_height - 100
        
        # Draw rounded rectangle with shadow
        shadow_offset = 8
        draw.rounded_rectangle(
            [badge_x + shadow_offset, badge_y + shadow_offset, 
             badge_x + badge_width + shadow_offset, badge_y + badge_height + shadow_offset],
            radius=25,
            fill=(0, 0, 0, 60)
        )
        
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
            radius=25,
            fill=badge_color
        )
        
        # Draw price
        text_color = ColorGenerator.ensure_contrast('#000000', palette.get('secondary'))
        draw.text((badge_x + 40, badge_y + 15), price_text, fill=text_color, font=font_price)
        draw.text((badge_x + 40, badge_y + 95), "FCFA", fill=text_color, font=font_currency)
        
        return image


class NewBadge(TemplateComponent):
    """'NEW' badge for products"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        # Create diagonal ribbon
        ribbon = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ribbon)
        
        # Ribbon color
        ribbon_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
        
        # Draw diagonal ribbon (top-left corner)
        points = [(0, 80), (180, 0), (220, 0), (0, 120)]
        draw.polygon(points, fill=ribbon_color + (255,))
        
        # Text
        try:
            font = ImageFont.truetype("arialbd.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Rotate text
        text_img = Image.new('RGBA', (150, 50), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((10, 5), "NEW!", fill='#FFFFFF', font=font)
