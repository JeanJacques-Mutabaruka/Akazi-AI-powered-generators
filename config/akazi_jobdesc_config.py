"""
AKAZI Job Description Configuration
Supports both English and French formats
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


class AkaziJobDescConfig(BaseConfig):
    """Configuration for AKAZI job description format"""
    
    def __init__(self, lang: str = 'en'):
        super().__init__()
        self.lang = lang
        
        # Century Gothic font (AKAZI standard)
        self.fonts = FontConfig(
            name="Century Gothic",
            size_body=10,
            size_title=11,
            size_header=11
        )
        
        # AKAZI color scheme
        self.colors = ColorConfig(
            black="000000",    # Default text, explicit information
            red="#C00000",      # Budget ONLY (DO NOT CHANGE)
            orange="FF8C00",   # Deduced/inferred information
            blue="0000FF"
        )
        
        # Spacing configuration
        self.spacing = SpacingConfig(
            before_heading=12,
            after_heading=6,
            between_paragraphs=6,
            after_header=12,
            line_spacing=1.0
        )
        
        # Indentation for bullet points
        self.indentation = IndentationConfig(
            level_1_indent=0.5,    # 0.5 inches
            level_2_indent=1.0,    # 1.0 inches
            hanging_indent=0.25    # 0.25 inches
        )
        
        # Bullet characters
        self.bullets = BulletConfig(
            level_1="*",
            level_2="-"
        )
        
        # Page margins
        self.margins = MarginConfig(
            top=1.0,
            right=1.0,
            bottom=1.0,
            left=1.0
        )
        
        # Default alignment
        self.alignment = "justify"
        
        # AKAZI specific rules
        self.akazi_rules = {
            "budget_color": "red",              # Budget ALWAYS in red
            "deduced_info_color": "orange",     # Deduced info in orange
            "explicit_info_color": "black",     # Explicit info in black
            "header_font_bold": True,           # Header always bold
            "section_headings_bold": True,      # Section titles always bold
            "anonymize_company": True,          # Anonymize company name
        }
        
        # Language-specific templates
        if lang == 'fr':
            self.anonymize_template = "Pour notre client dans le secteur {sector} basé au Rwanda"
        else:  # en
            self.anonymize_template = "For our client in the {sector} sector based in Rwanda"


def get_config(lang: str = 'en') -> dict:
    """
    Get AKAZI Job Description configuration
    
    Args:
        lang: Language code ('en' or 'fr')
    
    Returns:
        Configuration dictionary
    """
    config = AkaziJobDescConfig(lang)
    return config.to_dict()
