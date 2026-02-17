"""
Base Configuration Classes
Shared configuration utilities for all document formats
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from docx.shared import Pt, Inches, RGBColor


@dataclass
class FontConfig:
    """Font configuration"""
    name: str
    size_body: int = 10
    size_title: int = 11
    size_header: int = 11
    
    def get_size_pt(self, size_type: str = "body") -> Pt:
        """Get font size as Pt object"""
        size_map = {
            "body": self.size_body,
            "title": self.size_title,
            "header": self.size_header
        }
        return Pt(size_map.get(size_type, self.size_body))


@dataclass
class ColorConfig:
    """Color configuration (RGB hex codes)"""
    black: str = "000000"
    red: str = "FF0000"
    orange: str = "FF8C00"
    blue: str = "0000FF"
    
    def get_rgb(self, color_name: str) -> RGBColor:
        """Convert hex to RGBColor object"""
        hex_color = getattr(self, color_name, self.black)
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )


@dataclass
class SpacingConfig:
    """Spacing configuration (in points)"""
    before_heading: int = 12
    after_heading: int = 6
    between_paragraphs: int = 6
    after_header: int = 12
    line_spacing: float = 1.0
    
    def to_twips(self, spacing_type: str) -> int:
        """Convert points to twips (1pt = 20 twips)"""
        value = getattr(self, spacing_type, 0)
        return int(value * 20)


@dataclass
class IndentationConfig:
    """Indentation configuration (in inches)"""
    level_1_indent: float = 0.5
    level_2_indent: float = 1.0
    hanging_indent: float = 0.25
    
    def to_twips(self, indent_type: str) -> int:
        """Convert inches to twips (1 inch = 1440 twips)"""
        value = getattr(self, indent_type, 0)
        return int(value * 1440)
    
    def get_inches(self, indent_type: str) -> Inches:
        """Get indentation as Inches object"""
        value = getattr(self, indent_type, 0)
        return Inches(value)


@dataclass
class BulletConfig:
    """Bullet point configuration"""
    level_1: str = "*"
    level_2: str = "-"


@dataclass
class MarginConfig:
    """Page margin configuration (in inches)"""
    top: float = 1.0
    right: float = 1.0
    bottom: float = 1.0
    left: float = 1.0
    
    def to_twips(self, margin_type: str) -> int:
        """Convert inches to twips"""
        value = getattr(self, margin_type, 1.0)
        return int(value * 1440)
    
    def get_inches(self, margin_type: str) -> Inches:
        """Get margin as Inches object"""
        value = getattr(self, margin_type, 1.0)
        return Inches(value)


class BaseConfig:
    """
    Base configuration class
    All format-specific configs should inherit from this
    """
    
    def __init__(self):
        self.fonts = FontConfig(name="Arial")
        self.colors = ColorConfig()
        self.spacing = SpacingConfig()
        self.indentation = IndentationConfig()
        self.bullets = BulletConfig()
        self.margins = MarginConfig()
        self.alignment = "justify"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "fonts": self.fonts.__dict__,
            "colors": self.colors.__dict__,
            "spacing": self.spacing.__dict__,
            "indentation": self.indentation.__dict__,
            "bullets": self.bullets.__dict__,
            "margins": self.margins.__dict__,
            "alignment": self.alignment
        }
    
    def get_font_config(self) -> FontConfig:
        """Get font configuration"""
        return self.fonts
    
    def get_color_config(self) -> ColorConfig:
        """Get color configuration"""
        return self.colors
    
    def get_spacing_config(self) -> SpacingConfig:
        """Get spacing configuration"""
        return self.spacing
    
    def get_indentation_config(self) -> IndentationConfig:
        """Get indentation configuration"""
        return self.indentation
    
    def get_bullet_config(self) -> BulletConfig:
        """Get bullet configuration"""
        return self.bullets
    
    def get_margin_config(self) -> MarginConfig:
        """Get margin configuration"""
        return self.margins


# Helper functions for common operations
def pt_to_twips(points: float) -> int:
    """Convert points to twips (1pt = 20 twips)"""
    return int(points * 20)


def inch_to_twips(inches: float) -> int:
    """Convert inches to twips (1 inch = 1440 twips)"""
    return int(inches * 1440)


def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color string to RGBColor object"""
    hex_color = hex_color.lstrip('#')
    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )
