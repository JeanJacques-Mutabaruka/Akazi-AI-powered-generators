"""
MC2I CV Configuration (Dossier de Compétences)
Based on Prompt_optimise_transformation_CV_MC2I.md
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


class MC2ICVConfig(BaseConfig):
    """Configuration for MC2I competency dossier format"""
    
    def __init__(self):
        super().__init__()
        
        # Lato font (MC2I standard)
        # Fallback to Arial if Lato not available
        self.fonts = FontConfig(
            name="Lato",
            size_body=10,
            size_title=14,
            size_header=14
        )
        
        # MC2I specific color scheme (exact hex codes from prompt)
        self.colors = ColorConfig(
            black="575856",      # RGB(87, 88, 86) - Body text
            red="DD0061",        # RGB(221, 0, 97) - Company names
            orange="FF8C00",     # Inferred technologies
            blue="006A9E"        # RGB(0, 106, 158) - Position titles & periods
        )
        
        # Additional MC2I colors
        self.mc2i_colors = {
            "company": "DD0061",      # Company names - Small Caps
            "position": "006A9E",     # Position titles - Small Caps
            "period": "006A9E",       # Time periods - Small Caps
            "body_text": "575856",    # Regular text
            "keywords_bold": "575856",  # Bold keywords (Activités, Domaines, etc.)
            "inferred_tech": "FF8C00"   # Technologies not explicitly listed
        }
        
        # Spacing
        self.spacing = SpacingConfig(
            before_heading=12,
            after_heading=6,
            between_paragraphs=6,
            after_header=12,
            line_spacing=1.0
        )
        
        # Indentation
        self.indentation = IndentationConfig(
            level_1_indent=0.25,
            level_2_indent=0.5,
            hanging_indent=0.25
        )
        
        # Bullets
        self.bullets = BulletConfig(
            level_1="•",
            level_2="-"
        )
        
        # Margins
        self.margins = MarginConfig(
            top=1.0,
            right=1.0,
            bottom=1.0,
            left=1.0
        )
        
        # Alignment
        self.alignment = "justify"
        
        # MC2I-specific rules
        self.mc2i_rules = {
            # Font styles
            "company_style": "small_caps",
            "position_style": "small_caps",
            "period_style": "small_caps",
            "keywords_bold": True,
            
            # Required sections
            "require_summary_4_paragraphs": True,
            "summary_lengths": {
                "experience_summary": (200, 300),  # chars
                "technical_skills": (600, 850),    # chars
                "functional_skills": (200, 300),   # chars
                "conclusion": (200, 400)           # chars
            },
            
            # Period format
            "period_format": "MMMM YYYY",  # e.g., "Juillet 2023"
            "period_separator": " – ",      # En dash
            "period_ongoing_fr": "En cours",
            "period_ongoing_en": "Present",
            
            # Horizontal lines
            "section_separator_color": "DD0061",
            "separator_width_pt": 1,
            
            # Technology grouping
            "group_technologies": True,
            "infer_technologies": True,
            
            # Month translations (French)
            "french_months": {
                "January": "Janvier",
                "February": "Février",
                "March": "Mars",
                "April": "Avril",
                "May": "Mai",
                "June": "Juin",
                "July": "Juillet",
                "August": "Août",
                "September": "Septembre",
                "October": "Octobre",
                "November": "Novembre",
                "December": "Décembre"
            }
        }


def get_config() -> dict:
    """
    Get MC2I CV configuration
    
    Returns:
        Configuration dictionary
    """
    config = MC2ICVConfig()
    config_dict = config.to_dict()
    config_dict['mc2i_colors'] = config.mc2i_colors
    config_dict['mc2i_rules'] = config.mc2i_rules
    return config_dict
