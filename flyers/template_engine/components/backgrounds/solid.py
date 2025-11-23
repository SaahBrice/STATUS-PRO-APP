from PIL import Image
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator

class SolidBackground(TemplateComponent):
    """Create solid color background"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        bg_color = ColorGenerator.hex_to_rgb(palette.get('background', '#1A1A2E'))
        
        background = Image.new('RGB', (width, height), bg_color)
        
        if image.mode == 'RGBA':
            background = background.convert('RGBA')
            return Image.alpha_composite(background, image)
        
        return background
