from PIL import Image, ImageDraw, ImageFont
from ...base_component import TemplateComponent

class TextOutline(TemplateComponent):
    """Add outline to text"""
    
    def draw_text_with_outline(self, draw, position, text, font, fill, outline_color='#000000', outline_width=3):
        """Helper to draw outlined text"""
        x, y = position
        
        # Draw outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=fill)
    
    def apply(self, image, context):
        # This is a utility class
        return image
