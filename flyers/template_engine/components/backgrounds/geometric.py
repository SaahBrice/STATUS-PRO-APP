from PIL import Image, ImageDraw
import random
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator

class GeometricBackground(TemplateComponent):
    """Create geometric pattern background"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        bg_color = ColorGenerator.hex_to_rgb(palette.get('background', '#1A1A2E'))
        accent = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        
        background = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(background)
        
        # Draw random circles
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(100, 300)
            opacity = random.randint(10, 30)
            
            # Create semi-transparent circle
            circle_color = accent + (opacity,)
            temp = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp)
            temp_draw.ellipse([x - size, y - size, x + size, y + size], fill=circle_color)
            
            background = background.convert('RGBA')
            background = Image.alpha_composite(background, temp)
        
        return background.convert('RGB')
