from PIL import Image
import random
import json
import os
from pathlib import Path

from .color_generator import ColorGenerator
from .components.backgrounds import GradientBackground, SolidBackground, GeometricBackground
from .layouts import CenteredLayout, SplitLayout
from .layouts.hero_product import HeroProductLayout
from .layouts.minimal_elegant import MinimalElegantLayout
from .layouts.dynamic_diagonal import DynamicDiagonalLayout
from .layouts.dynamic_diagonal import DynamicDiagonalLayout
from .layouts.magazine_style import MagazineStyleLayout
from .layouts.neon_glow import NeonGlowLayout

class TemplateGenerator:
    """Main template generation engine with multi-layout support"""
    
    BACKGROUND_MAP = {
        'gradient': GradientBackground,
        'solid': SolidBackground,
        'geometric': GeometricBackground
    }
    
    LAYOUT_MAP = {
        'centered': CenteredLayout,
        'split': SplitLayout,
        'hero': HeroProductLayout,
        'minimal': MinimalElegantLayout,
        'diagonal': DynamicDiagonalLayout,
        'magazine': MagazineStyleLayout,
        'neon': NeonGlowLayout
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
    
    def generate_templates(self, product, templates_per_layout=1):
        """
        Generate multiple template designs using ALL available layouts
        
        Args:
            product: Product model instance
            templates_per_layout: How many variations per layout (default: 1)
        
        Returns:
            List of PIL Image objects
        """
        templates = []
        dimensions = self.get_dimensions(product.output_format)
        
        # Get all available layouts
        all_layouts = list(self.LAYOUT_MAP.keys())
        
        # Generate templates for each layout
        for layout_name in all_layouts:
            for variation in range(templates_per_layout):
                # Select a theme (cycle through themes)
                theme_index = (len(templates) % len(self.themes))
                theme = self.themes[theme_index]
                
                # Generate template with this layout
                template = self.generate_single_template(
                    product, 
                    theme, 
                    dimensions,
                    force_layout=layout_name,
                    variation_seed=variation
                )
                templates.append(template)
        
        return templates
    
    def generate_single_template(self, product, theme, dimensions, force_layout=None, variation_seed=0):
        """Generate a single template with specific layout"""
        width, height = dimensions
        
        # Create base image
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        
        # Get color palette (vary if multiple variations)
        palette = ColorGenerator.get_palette(theme['category'])
        
        # Context for components
        context = {
            'product': product,
            'color_palette': palette,
            'theme': theme,
            'dimensions': dimensions,
            'variation': variation_seed
        }
        
        # Apply background (vary based on seed)
        available_backgrounds = theme.get('backgrounds', ['gradient', 'solid'])
        bg_type = available_backgrounds[variation_seed % len(available_backgrounds)]
        
        if bg_type in self.BACKGROUND_MAP:
            background_component = self.BACKGROUND_MAP[bg_type]()
            image = background_component.apply(image, context)
        
        # Apply layout (use forced layout or random from theme)
        if force_layout and force_layout in self.LAYOUT_MAP:
            layout_type = force_layout
        else:
            layout_type = random.choice(theme.get('layouts', ['centered']))
        
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
    
    def get_layout_count(self):
        """Return total number of available layouts"""
        return len(self.LAYOUT_MAP)
