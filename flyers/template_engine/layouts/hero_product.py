from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
from ..components.decorations.badges import DiscountBadge, PriceBadge
from ..components.decorations.shapes import CircleDecoration
import textwrap

class HeroProductLayout(TemplateComponent):
    """Modern hero-style layout with large product focus"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        # Apply decorative circles first
        circle_decoration = CircleDecoration()
        image = circle_decoration.apply(image, context)
        
        draw = ImageDraw.Draw(image)
        
        # Load fonts
        try:
            font_name = ImageFont.truetype("arialbd.ttf", 85)
            font_price = ImageFont.truetype("arialbd.ttf", 100)
            font_desc = ImageFont.truetype("arial.ttf", 38)
            font_info = ImageFont.truetype("arial.ttf", 32)
            font_cta = ImageFont.truetype("arialbd.ttf", 45)
            font_discount = ImageFont.truetype("arialbd.ttf", 38)
        except:
            font_name = font_price = font_desc = font_info = font_cta = font_discount = ImageFont.load_default()
        
        # === HERO PRODUCT IMAGE (Center, Large) ===
        product_img = Image.open(product.original_image.path).convert('RGBA')
        
        # Make it HUGE - 70% of width
        img_max_width = int(width * 0.70)
        img_max_height = int(height * 0.45)
        product_img.thumbnail((img_max_width, img_max_height), Image.LANCZOS)
        
        # Add professional shadow
        shadow = Image.new('RGBA', (product_img.width + 40, product_img.height + 40), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_color = (0, 0, 0, 80)
        shadow_draw.rounded_rectangle([0, 0, shadow.width, shadow.height], radius=20, fill=shadow_color)
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        
        # Position
        img_x = (width - product_img.width) // 2
        img_y = int(height * 0.15)
        
        # Paste shadow and image
        image.paste(shadow, (img_x - 20, img_y - 20), shadow)
        image.paste(product_img, (img_x, img_y), product_img)
        
        # === DISCOUNT BADGE (if exists) ===
        if product.discount_message:
            badge_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            badge_draw = ImageDraw.Draw(badge_img)
            
            # Create eye-catching badge
            badge_text = product.discount_message.upper()
            badge_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#FF3366'))
            
            # Positioned at top-right of product image
            badge_x = img_x + product_img.width - 180
            badge_y = img_y - 30
            
            # Draw starburst shape
            badge_draw.ellipse([badge_x, badge_y, badge_x + 180, badge_y + 180], fill=badge_color + (255,))
            
            # Inner glow
            glow_color = tuple(min(c + 60, 255) for c in badge_color)
            badge_draw.ellipse([badge_x + 25, badge_y + 25, badge_x + 155, badge_y + 155], fill=glow_color + (255,))
            
            # Text
            bbox = badge_draw.textbbox((0, 0), badge_text, font=font_discount)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            badge_draw.text((badge_x + (180 - text_w) // 2, badge_y + (180 - text_h) // 2 - 10), 
                          badge_text, fill='#FFFFFF', font=font_discount)
            
            image = Image.alpha_composite(image.convert('RGBA'), badge_img).convert('RGB')
        
        text_y = img_y + product_img.height + 50
        text_color = palette.get('text', '#FFFFFF')
        
        # === PRODUCT NAME (Bold, Center) ===
        name = (product.name or "Product").upper()
        name_lines = textwrap.wrap(name, width=18)
        
        for line in name_lines[:2]:
            # Draw text with subtle shadow
            bbox = draw.textbbox((0, 0), line, font=font_name)
            text_width = bbox[2] - bbox[0]
            
            # Shadow
            for offset in range(1, 5):
                draw.text(((width - text_width) // 2 + offset, text_y + offset), 
                         line, fill='#000000', font=font_name)
            
            # Main text
            draw.text(((width - text_width) // 2, text_y), line, fill=text_color, font=font_name)
            text_y += 95
        
        text_y += 30
        
        # === PRICE (Huge, Center, with Badge Background) ===
        price_text = f"{int(product.price or 0):,}"
        price_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#FFD700'))
        
        bbox = draw.textbbox((0, 0), price_text, font=font_price)
        price_width = bbox[2] - bbox[0] + 70
        price_height = 130
        
        badge_x = (width - price_width) // 2
        badge_y = text_y
        
        # Draw price badge with gradient effect
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + price_width, badge_y + price_height],
            radius=25,
            fill=price_color
        )
        
        # Price text
        price_text_color = ColorGenerator.ensure_contrast('#000000', palette.get('secondary'))
        draw.text((badge_x + 35, badge_y + 10), price_text, fill=price_text_color, font=font_price)
        
        # FCFA label
        draw.text((badge_x + 20, badge_y + 95), "FCFA", fill=price_text_color, font=ImageFont.truetype("arialbd.ttf", 35) if True else font_info)
        
        text_y += price_height + 50
        
        # === DESCRIPTION ===
        if product.description:
            desc = product.description[:100] + "..." if len(product.description) > 100 else product.description
            desc_lines = textwrap.wrap(desc, width=35)
            
            for line in desc_lines[:2]:
                bbox = draw.textbbox((0, 0), line, font=font_desc)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, text_y), line, fill=text_color, font=font_desc)
                text_y += 48
            
            text_y += 30
        
        # === BOTTOM INFO SECTION (Icons + Text) ===
        bottom_y = height - 250
        
        if product.contact_info:
            contact = f"📞 {product.contact_info}"
            contact_lines = textwrap.wrap(contact, width=30)
            for line in contact_lines[:1]:
                bbox = draw.textbbox((0, 0), line, font=font_info)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, bottom_y), line, fill=text_color, font=font_info)
            bottom_y += 50
        
        if product.delivery_info:
            delivery = f"🚚 {product.delivery_info}"
            delivery_lines = textwrap.wrap(delivery, width=30)
            for line in delivery_lines[:1]:
                bbox = draw.textbbox((0, 0), line, font=font_info)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, bottom_y), line, fill=text_color, font=font_info)
            bottom_y += 60
        
        # === CALL TO ACTION (Prominent Button) ===
        if product.call_to_action:
            cta_text = product.call_to_action.upper()
            cta_bg = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
            
            bbox = draw.textbbox((0, 0), cta_text, font=font_cta)
            cta_width = bbox[2] - bbox[0] + 80
            cta_height = 85
            cta_x = (width - cta_width) // 2
            cta_y = bottom_y
            
            # Button shadow
            draw.rounded_rectangle(
                [cta_x + 6, cta_y + 6, cta_x + cta_width + 6, cta_y + cta_height + 6],
                radius=30,
                fill=(0, 0, 0, 100)
            )
            
            # Button
            draw.rounded_rectangle(
                [cta_x, cta_y, cta_x + cta_width, cta_y + cta_height],
                radius=30,
                fill=cta_bg
            )
            
            # Text
            draw.text((cta_x + 40, cta_y + 18), cta_text, fill='#FFFFFF', font=font_cta)
        
        return image
