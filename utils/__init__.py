"""
Utils package for AKAZI Generator.
Provides utilities for logging, validation, performance tracking, etc.
"""

# Import key functions for easy access
from utils.logger import get_logger
from utils.validator import DocumentValidator
from utils.file_handler import FileHandler
from utils.performance import PerformanceTracker

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
    'get_logger',
    'DocumentValidator',
    'FileHandler',
    'PerformanceTracker',
    'init_session_state',
    'cache_generation_result',
    'get_generation_history',
    'get_error_history',
    'calculate_statistics',
    'update_statistics',
    'clear_cache'
]