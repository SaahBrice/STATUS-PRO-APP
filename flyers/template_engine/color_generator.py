import random
import colorsys

class ColorGenerator:
    """Generate harmonious color palettes"""
    
    # Pre-defined color schemes
    SCHEMES = {
        'bold': [
            {'primary': '#FF3366', 'secondary': '#FFD700', 'background': '#1A1A2E', 'text': '#FFFFFF'},
            {'primary': '#00D9FF', 'secondary': '#FF006E', 'background': '#0A0E27', 'text': '#FFFFFF'},
            {'primary': '#FF6B35', 'secondary': '#F7931E', 'background': '#1B2431', 'text': '#FFFFFF'},
        ],
        'elegant': [
            {'primary': '#C9ADA7', 'secondary': '#9A8C98', 'background': '#22223B', 'text': '#F2E9E4'},
            {'primary': '#B8A9C9', 'secondary': '#A991C4', 'background': '#2B2D42', 'text': '#EDF2F4'},
            {'primary': '#E5989B', 'secondary': '#B5838D', 'background': '#1D3557', 'text': '#F1FAEE'},
        ],
        'modern': [
            {'primary': '#06FFA5', 'secondary': '#00D4AA', 'background': '#0D1B2A', 'text': '#FFFFFF'},
            {'primary': '#7209B7', 'secondary': '#F72585', 'background': '#000000', 'text': '#FFFFFF'},
            {'primary': '#4361EE', 'secondary': '#4CC9F0', 'background': '#0B090A', 'text': '#FFFFFF'},
        ]
    }
    
    @classmethod
    def get_palette(cls, theme_category):
        """Get a random color palette for a theme category"""
        if theme_category in cls.SCHEMES:
            return random.choice(cls.SCHEMES[theme_category])
        return cls.SCHEMES['modern'][0]
    
    @classmethod
    def hex_to_rgb(cls, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @classmethod
    def ensure_contrast(cls, text_color, bg_color):
        """Ensure text is readable on background"""
        # Simple contrast check - return white or black text
        bg_rgb = cls.hex_to_rgb(bg_color) if isinstance(bg_color, str) else bg_color
        brightness = (bg_rgb[0] * 299 + bg_rgb[1] * 587 + bg_rgb[2] * 114) / 1000
        return '#FFFFFF' if brightness < 128 else '#000000'
