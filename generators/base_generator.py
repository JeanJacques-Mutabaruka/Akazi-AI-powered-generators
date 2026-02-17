"""
Base Generator - Abstract class for all document generators
FIXED VERSION - Corrects constructor signature and data loading
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from io import BytesIO
import json
import yaml

from utils.logger import logger
from utils.validator import DocumentValidator
from utils.performance import PerformanceTracker


class BaseGenerator(ABC):
    """
    Abstract base class for all document generators
    
    Implements the Template Method pattern:
    - Defines the skeleton of document generation
    - Leaves specific steps to subclasses
    """
    
    def __init__(
        self,
        input_file: Path,
        output_file: Path,
        lang: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize generator
        
        Args:
            input_file: Path to input JSON/YAML file
            output_file: Path to output document file
            lang: Optional language code (default: 'en')
            **kwargs: Additional parameters for subclasses
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.lang = lang or 'en'
        self.data: Optional[Dict[str, Any]] = None
        
        # Initialize utilities
        self.validator = DocumentValidator()
        self.performance_tracker = PerformanceTracker()
        
        # Validate input file exists
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        logger.debug(
            "generator_initialized",
            generator=self.__class__.__name__,
            input_file=str(self.input_file),
            output_file=str(self.output_file)
        )
    
    def load_data(self) -> Dict[str, Any]:
        """
        Load and parse input JSON/YAML file
        
        Returns:
            Parsed data dictionary
            
        Raises:
            ValueError: If file format is invalid
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                if self.input_file.suffix.lower() in ['.yaml', '.yml']:
                    self.data = yaml.safe_load(f)
                    logger.info("yaml_data_loaded", file=self.input_file.name)
                else:
                    self.data = json.load(f)
                    logger.info("json_data_loaded", file=self.input_file.name)
            
            if not isinstance(self.data, dict):
                raise ValueError("Data must be a dictionary")
            
            return self.data
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error("data_parse_error", file=self.input_file.name, error=str(e))
            raise ValueError(f"Failed to parse file: {e}")
        except Exception as e:
            logger.error("data_load_error", file=self.input_file.name, error=str(e))
            raise
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data structure (implementation-specific)
        
        Args:
            data: Data to validate
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If data is invalid
        """
        pass
    
    @abstractmethod
    def setup_document(self):
        """
        Initialize document with formatting
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def generate_content(self):
        """
        Generate document content
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def save_document(self):
        """
        Save the generated document
        Must be implemented by subclasses
        """
        pass
    
    def generate(self) -> Path:
        """
        Main method to generate document (Template Method)
        
        Workflow:
        1. Load data from input file
        2. Validate data
        3. Setup document
        4. Generate content
        5. Save document
        
        Returns:
            Path to generated document
            
        Raises:
            Exception: If any step fails
        """
        try:
            logger.info(
                "generation_started",
                generator=self.__class__.__name__,
                input_file=self.input_file.name
            )
            
            # Step 1: Load data
            if self.data is None:
                self.load_data()
            
            # Step 2: Validate
            self.validate_data(self.data)
            
            # Step 3: Setup document
            self.setup_document()
            
            # Step 4: Generate content
            self.generate_content()
            
            # Step 5: Save
            self.save_document()
            
            logger.info(
                "generation_completed",
                generator=self.__class__.__name__,
                output_file=self.output_file.name
            )
            
            return self.output_file
            
        except Exception as e:
            logger.error(
                "generation_failed",
                generator=self.__class__.__name__,
                error=str(e)
            )
            raise
    
    def generate_to_buffer(self) -> BytesIO:
        """
        Generate document to BytesIO buffer instead of file
        
        Returns:
            BytesIO buffer with document content
        """
        # Generate to file first
        self.generate()
        
        # Read file into buffer
        buffer = BytesIO()
        with open(self.output_file, 'rb') as f:
            buffer.write(f.read())
        buffer.seek(0)
        
        return buffer
