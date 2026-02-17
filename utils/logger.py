"""
Structured Logging Module
Provides JSON-formatted logs for better analysis and debugging
"""

import logging
import structlog
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import sys


class LoggerSetup:
    """Configure structured logging for the application"""
    
    _initialized = False
    _logger = None
    
    @classmethod
    def get_logger(cls, name: str = "akazi_generator"):
        """
        Get or create a structured logger
        
        Args:
            name: Logger name
        
        Returns:
            Configured structlog logger
        """
        if not cls._initialized:
            cls._setup_logging()
            cls._initialized = True
        
        return structlog.get_logger(name)
    
    @classmethod
    def _setup_logging(cls):
        """Configure structlog with processors and handlers"""
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            level=logging.INFO,
            handlers=[
                # All logs
                logging.FileHandler(
                    logs_dir / "processing.log",
                    encoding='utf-8'
                ),
                # Error logs only
                logging.FileHandler(
                    logs_dir / "errors.log",
                    encoding='utf-8'
                ),
                # Console output (for development)
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set error-only filter for errors.log
        error_handler = logging.getLogger().handlers[1]
        error_handler.setLevel(logging.ERROR)
        
        # Configure structlog processors
        structlog.configure(
            processors=[
                # Add timestamp
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                
                # Add log level
                structlog.processors.add_log_level,
                
                # Add logger name
                structlog.processors.CallsiteParameterAdder(
                    [
                        structlog.processors.CallsiteParameter.FILENAME,
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    ]
                ),
                
                # Stack info for exceptions
                structlog.processors.StackInfoRenderer(),
                
                # Exception formatting
                structlog.processors.format_exc_info,
                
                # JSON output
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    
    @classmethod
    def log_file_operation(
        cls,
        operation: str,
        filename: str,
        status: str,
        **kwargs
    ):
        """
        Convenience method for logging file operations
        
        Args:
            operation: Operation type (e.g., 'upload', 'generate', 'download')
            filename: File being processed
            status: Status (e.g., 'started', 'completed', 'failed')
            **kwargs: Additional context
        """
        logger = cls.get_logger()
        
        log_data = {
            "operation": operation,
            "filename": filename,
            "status": status,
            **kwargs
        }
        
        if status == "failed":
            logger.error(f"file_{operation}_{status}", **log_data)
        else:
            logger.info(f"file_{operation}_{status}", **log_data)
    
    @classmethod
    def log_performance(
        cls,
        metric_name: str,
        value: float,
        unit: str = "seconds",
        **kwargs
    ):
        """
        Log performance metrics
        
        Args:
            metric_name: Metric name (e.g., 'generation_time')
            value: Metric value
            unit: Unit of measurement
            **kwargs: Additional context
        """
        logger = cls.get_logger()
        logger.info(
            "performance_metric",
            metric=metric_name,
            value=value,
            unit=unit,
            **kwargs
        )


# Global logger instance
logger = LoggerSetup.get_logger()


# Convenience functions
def log_info(event: str, **kwargs):
    """Log info-level event"""
    logger.info(event, **kwargs)


def log_error(event: str, **kwargs):
    """Log error-level event"""
    logger.error(event, **kwargs)


def log_warning(event: str, **kwargs):
    """Log warning-level event"""
    logger.warning(event, **kwargs)


def log_debug(event: str, **kwargs):
    """Log debug-level event"""
    logger.debug(event, **kwargs)

# Convenience function for direct import
def get_logger(name: str = "akazi_generator"):
    """Wrapper function for easy import"""
    return LoggerSetup.get_logger(name)