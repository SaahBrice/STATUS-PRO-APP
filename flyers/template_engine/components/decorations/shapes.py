from PIL import Image, ImageDraw
import random
from ...base_component import TemplateComponent
from ...color_generator import ColorGenerator

class CircleDecoration(TemplateComponent):
    """Decorative circles in background"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        accent = ColorGenerator.hex_to_rgb(palette.get('primary', '#6366F1'))
        
        # Draw 3-5 decorative circles
        for _ in range(random.randint(3, 5)):
            x = random.randint(-100, width + 100)
            y = random.randint(-100, height + 100)
            size = random.randint(150, 400)
            opacity = random.randint(5, 15)
            
            color = accent + (opacity,)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        
        return Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')


class PolygonDecoration(TemplateComponent):
    """Decorative geometric shapes"""
    
    def apply(self, image, context):
        width, height = image.size
        palette = context.get('color_palette', {})
        
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        accent = ColorGenerator.hex_to_rgb(palette.get('secondary', '#8B5CF6'))
        
        # Draw triangles in corners
        opacity = 20
        color = accent + (opacity,)
        
        # Top-right triangle
        points = [(width, 0), (width - 300, 0), (width, 300)]
        draw.polygon(points, fill=color)
        
        # Bottom-left triangle
        points = [(0, height), (300, height), (0, height - 300)]
        draw.polygon
