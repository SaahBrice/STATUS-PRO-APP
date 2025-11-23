from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ...base_component import TemplateComponent

class TextShadow(TemplateComponent):
    """Add shadow effect to text for better readability"""
    
    def draw_text_with_shadow(self, draw, position, text, font, fill, shadow_color='#000000'):
        """Helper to draw text with shadow"""
        x, y = position
        
        # Draw shadow (offset)
        for offset in range(1, 4):
            draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)
    
    def apply(self, image, context):
        # This is a utility class, not directly applied
        return image
