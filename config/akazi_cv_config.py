"""
AKAZI CV Configuration
Based on Prompt_Transformation_CV_AKAZI__V3.md
FIXED VERSION - Uses absolute imports
"""

from config.base_config import (
    BaseConfig,
    FontConfig,
    ColorConfig,
    SpacingConfig,
    IndentationConfig,
    BulletConfig,
    MarginConfig
)


class AkaziCVConfig(BaseConfig):
    """Configuration for AKAZI CV format"""
    
    def __init__(self):
        super().__init__()
        
        # Century Gothic font (same as AKAZI Job Desc)
        self.fonts = FontConfig(
            name="Century Gothic",
            size_body=10,
            size_title=12,
            size_header=14
        )
        
        # AKAZI CV color scheme
        self.colors = ColorConfig(
            black="000000",    # Regular text
            red="DD0061",      # Can be used for headers/emphasis
            orange="FF8C00",   # Inferred information
            blue="006A9E"      # Accent color
        )
        
        # Spacing
        self.spacing = SpacingConfig(
            before_heading=10,
            after_heading=4,
            between_paragraphs=6,
            after_header=10,
            line_spacing=1.15
        )
        
        # Indentation
        self.indentation = IndentationConfig(
            level_1_indent=0.3,
            level_2_indent=0.6,
            hanging_indent=0.2
        )
        
        # Bullets
        self.bullets = BulletConfig(
            level_1="•",
            level_2="◦"
        )
        
        # Margins
        self.margins = MarginConfig(
            top=0.75,
            right=0.75,
            bottom=0.75,
            left=0.75
        )
        
        # Alignment
        self.alignment = "left"
        
        # CV-specific settings
        self.cv_settings = {
            "header_name_size": 16,
            "header_title_size": 12,
            "section_title_size": 11,
            "show_contact_icons": False,
            "date_format": "%Y-%m",  # YYYY-MM
            "calculate_duration": True,
            "group_skills_by_category": True
        }


def get_config() -> dict:
    """
    Get AKAZI CV configuration
    
    Returns:
        Configuration dictionary
    """
    config = AkaziCVConfig()
    config_dict = config.to_dict()
    config_dict['cv_settings'] = config.cv_settings
    return config_dict
