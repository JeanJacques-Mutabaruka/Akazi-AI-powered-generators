"""
Configuration Package
Format-specific configurations for document generation
"""

from .base_config import (
    BaseConfig,
    FontConfig,
    ColorConfig,
    SpacingConfig,
    IndentationConfig,
    BulletConfig,
    MarginConfig,
    pt_to_twips,
    inch_to_twips,
    hex_to_rgb
)

__all__ = [
    'BaseConfig',
    'FontConfig',
    'ColorConfig',
    'SpacingConfig',
    'IndentationConfig',
    'BulletConfig',
    'MarginConfig',
    'pt_to_twips',
    'inch_to_twips',
    'hex_to_rgb',
]
