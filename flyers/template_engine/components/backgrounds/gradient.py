from PIL import Image, ImageDraw
import numpy as np
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator

class GradientBackground(TemplateComponent):
    """Create gradient background"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        primary = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        secondary = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        
        # Create gradient
        gradient = Image.new('RGB', (width, height), primary)
        draw = ImageDraw.Draw(gradient)
        
        # Vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(primary[0] * (1 - ratio) + secondary[0] * ratio)
            g = int(primary[1] * (1 - ratio) + secondary[1] * ratio)
            b = int(primary[2] * (1 - ratio) + secondary[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Composite with original if it has content
        if image.mode == 'RGBA':
            gradient = gradient.convert('RGBA')
            return Image.alpha_composite(gradient, image)
        
        return gradient
