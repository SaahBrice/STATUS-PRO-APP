from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..base_component import TemplateComponent
from ..color_generator import ColorGenerator
import textwrap

class MinimalElegantLayout(TemplateComponent):
    """Clean, minimal, elegant design with lots of white space"""
    
    def apply(self, image, context):
        width, height = image.size
        product = context.get('product')
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Fonts
        try:
            font_name = ImageFont.truetype("arial.ttf", 75)
            font_price = ImageFont.truetype("arialbd.ttf", 110)
            font_desc = ImageFont.truetype("arial.ttf", 34)
            font_info = ImageFont.truetype("arial.ttf", 28)
            font_label = ImageFont.truetype("arial.ttf", 30)
        except:
            font_name = font_price = font_desc = font_info = font_label = ImageFont.load_default()
        
        # === THIN TOP ACCENT LINE ===
        accent_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        draw.rectangle([0, 0, width, 8], fill=accent_color)
        
        text_y = 80
        text_color = palette.get('text', '#FFFFFF')
        
        # === PRODUCT NAME (Thin, Elegant) ===
        name = product.name or "Product"
        name_lines = textwrap.wrap(name, width=22)
        
        for line in name_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=font_name)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, text_y), line.upper(), fill=text_color, font=font_name)
            text_y += 85
        
        text_y += 40
        
        # === PRODUCT IMAGE (Square, Centered) ===
        product_img = Image.open(product.original_image.path).convert('RGBA')
        
        # Square crop and resize
        min_dim = min(product_img.width, product_img.height)
        left = (product_img.width - min_dim) // 2
        top = (product_img.height - min_dim) // 2
        product_img = product_img.crop((left, top, left + min_dim, top + min_dim))
        
        img_size = int(width * 0.60)
        product_img = product_img.resize((img_size, img_size), Image.LANCZOS)
        
        img_x = (width - img_size) // 2
        img_y = text_y
        
        # Subtle border around image
        border_color = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        draw.rounded_rectangle(
            [img_x - 5, img_y - 5, img_x + img_size + 5, img_y + img_size + 5],
            radius=15,
            outline=border_color,
            width=3
        )
        
        image.paste(product_img, (img_x, img_y), product_img)
        
        text_y = img_y + img_size + 50
        
        # === PRICE (Large, Bold) ===
        price_num = f"{int(product.price or 0):,}"
        
        bbox = draw.textbbox((0, 0), price_num, font=font_price)
        text_width = bbox[2] - bbox[0]
        
        price_x = (width - text_width) // 2
        draw.text((price_x, text_y), price_num, fill=accent_color, font=font_price)
        
        # FCFA below
        fcfa_bbox = draw.textbbox((0, 0), "FCFA", font=font_label)
        fcfa_width = fcfa_bbox[2] - fcfa_bbox[0]
        draw.text(((width - fcfa_width) // 2, text_y + 120), "FCFA", fill=text_color, font=font_label)
        
        text_y += 200
        
        # === DISCOUNT (if exists) ===
        if product.discount_message:
            disc_text = f"• {product.discount_message} •"
            bbox = draw.textbbox((0, 0), disc_text, font=font_desc)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, text_y), disc_text, fill=accent_color, font=font_desc)
            text_y += 50
        
        # === DESCRIPTION ===
        if product.description:
            desc = product.description[:90] + "..." if len(product.description) > 90 else product.description
            desc_lines = textwrap.wrap(desc, width=32)
            
            for line in desc_lines[:2]:
                bbox = draw.textbbox((0, 0), line, font=font_desc)
                text_width = bbox[2] - bbox[0]
                draw.text(((width - text_width) // 2, text_y), line, fill=text_color, font=font_desc)
                text_y += 45
        
        # === BOTTOM INFO (Minimal) ===
        bottom_y = height - 200
        
        info_items = []
        if product.contact_info:
            info_items.append(product.contact_info)
        if product.delivery_info:
            info_items.append(product.delivery_info)
        
        for item in info_items[:2]:
            bbox = draw.textbbox((0, 0), item, font=font_info)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, bottom_y), item, fill=text_color, font=font_info)
            bottom_y += 40
        
        # === THIN BOTTOM LINE ===
        draw.rectangle([0, height - 8, width, height], fill=accent_color)
        
        return image
