from PIL import Image
import random
import json
import os
from pathlib import Path

from .color_generator import ColorGenerator
from .components.backgrounds import GradientBackground, SolidBackground, GeometricBackground
from .layouts import CenteredLayout, SplitLayout

class TemplateGenerator:
    """Main template generation engine"""
    
    BACKGROUND_MAP = {
        'gradient': GradientBackground,
        'solid': SolidBackground,
        'geometric': GeometricBackground
    }
    
    LAYOUT_MAP = {
        'centered': CenteredLayout,
        'split': SplitLayout
    }
    
    def __init__(self):
        self.themes_path = Path(__file__).parent / 'themes'
        self.themes = self.load_themes()
    
    def load_themes(self):
        """Load all enabled themes from JSON files"""
        themes = []
        for theme_file in self.themes_path.glob('*.json'):
            with open(theme_file, 'r') as f:
                theme = json.load(f)
                if theme.get('enabled', True):
                    themes.append(theme)
        return themes
    
    def generate_templates(self, product, count=3):
        """
        Generate multiple template designs for a product
        
        Args:
            product: Product model instance
            count: Number of templates to generate
        
        Returns:
            List of PIL Image objects
        """
        templates = []
        used_themes = set()
        
        # Get dimensions based on output format
        dimensions = self.get_dimensions(product.output_format)
        
        for i in range(count):
            # Select a unique theme
            available_themes = [t for t in self.themes if t['name'] not in used_themes]
            if not available_themes:
                available_themes = self.themes  # Reset if all used
                used_themes.clear()
            
            theme = random.choice(available_themes)
            used_themes.add(theme['name'])
            
            # Generate template
            template = self.generate_single_template(product, theme, dimensions)
            templates.append(template)
        
        return templates
    
    def generate_single_template(self, product, theme, dimensions):
        """Generate a single template"""
        width, height = dimensions
        
        # Create base image
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        
        # Get color palette
        palette = ColorGenerator.get_palette(theme['category'])
        
        # Context for components
        context = {
            'product': product,
            'color_palette': palette,
            'theme': theme,
            'dimensions': dimensions
        }
        
        # Apply background
        bg_type = random.choice(theme['backgrounds'])
        if bg_type in self.BACKGROUND_MAP:
            background_component = self.BACKGROUND_MAP[bg_type]()
            image = background_component.apply(image, context)
        
        # Apply layout
        layout_type = random.choice(theme['layouts'])
        if layout_type in self.LAYOUT_MAP:
            layout_component = self.LAYOUT_MAP[layout_type]()
            image = layout_component.apply(image, context)
        
        return image.convert('RGB')
    
    def get_dimensions(self, output_format):
        """Get dimensions based on output format"""
        dimensions_map = {
            'square': (1080, 1080),
            'portrait': (1080, 1920),
            'landscape': (1920, 1080)
        }
        return dimensions_map.get(output_format, (1080, 1080))
