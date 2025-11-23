from abc import ABC, abstractmethod
from PIL import Image

class TemplateComponent(ABC):
    """Base class for all template components"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.enabled = True
    
    @abstractmethod
    def apply(self, image, context):
        """
        Apply this component to the image
        
        Args:
            image: PIL Image object
            context: dict with product data, dimensions, etc.
        
        Returns:
            Modified PIL Image object
        """
        pass
    
    def can_combine_with(self, other_component):
        """Check if this component is compatible with another"""
        return True
