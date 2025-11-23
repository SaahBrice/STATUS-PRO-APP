from PIL import Image, ImageDraw
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator

class RoundedFrame(TemplateComponent):
    """Rounded frame around entire design"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Frame color
        frame_color = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        
        # Draw thick rounded border
        border_width = 15
        draw.rounded_rectangle(
            [border_width, border_width, width - border_width, height - border_width],
            radius=30,
            outline=frame_color,
            width=border_width
        )
        
        return image


class BorderFrame(TemplateComponent):
    """Simple border frame"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        draw = ImageDraw.Draw(image)
        
        # Double border effect
        color1 = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        color2 = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        
        # Outer border
        draw.rectangle([20, 20, width - 20, height - 20], outline=color1, width=8)
        
        # Inner border
        draw.rectangle([35, 35, width - 35, height - 35], outline=color2, width=4)
        
        return image
