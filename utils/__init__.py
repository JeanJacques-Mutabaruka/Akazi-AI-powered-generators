"""
Utils package for AKAZI Generator.
Provides utilities for logging, validation, performance tracking,
document styling and layout management.
"""

# Logging
from utils.logger import get_logger

# Validation
from utils.validator import DocumentValidator

# File handling
from utils.file_handler import FileHandler

# Performance tracking
from utils.performance import PerformanceTracker

# Document styling & layout (AKAZI corporate)
from utils.akazi_styles import AkaziStyleManager
from utils.akazi_layout import AkaziLayoutManager

# Document layout (MC2I corporate)
from utils.mc2i_layout import MC2ILayoutManager

# Cache manager functions
from utils.cache_manager import (
    init_session_state,
    cache_generation_result,
    get_generation_history,
    get_error_history,
    calculate_statistics,
    update_statistics,
    clear_cache
)

__all__ = [
    # Logging
    'get_logger',
    # Validation & file handling
    'DocumentValidator',
    'FileHandler',
    # Performance
    'PerformanceTracker',
    # Document styling & layout
    'AkaziStyleManager',
    'AkaziLayoutManager',
    'MC2ILayoutManager',
    # Cache / session
    'init_session_state',
    'cache_generation_result',
    'get_generation_history',
    'get_error_history',
    'calculate_statistics',
    'update_statistics',
    'clear_cache',
]
