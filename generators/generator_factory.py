"""
Generator Factory - Factory pattern with lazy loading and singleton.
Creates appropriate generator instances based on document type.
FIXED VERSION - Corrects validation method call
"""

from typing import Dict, Optional, Type
from pathlib import Path
import json
import yaml
from utils.logger import get_logger
from utils.validator import DocumentValidator
from generators.base_generator import BaseGenerator

logger = get_logger(__name__)


class GeneratorFactory:
    """
    Factory class for creating document generators using lazy loading.
    Implements singleton pattern for generator class caching.
    """
    
    _generator_classes: Dict[str, Type[BaseGenerator]] = {}
    _loaded_modules: Dict[str, bool] = {}
    
    # Mapping of document types to generator class names
    GENERATOR_MAP = {
        'akazi_jobdesc': 'AkaziJobDescGenerator',
        'akazi_cv': 'AkaziCVGenerator',
        'mc2i_cv': 'MC2ICVGenerator'
    }
    
    # Mapping of generator class names to module paths
    MODULE_MAP = {
        'AkaziJobDescGenerator': 'generators.akazi_jobdesc_generator',
        'AkaziCVGenerator': 'generators.akazi_cv_generator',
        'MC2ICVGenerator': 'generators.mc2i_cv_generator'
    }
    
    @classmethod
    def _load_generator_class(cls, generator_name: str) -> Type[BaseGenerator]:
        """
        Lazy load generator class on first use.
        
        Args:
            generator_name: Name of the generator class
            
        Returns:
            Generator class type
            
        Raises:
            ImportError: If generator module cannot be imported
            AttributeError: If generator class not found in module
        """
        if generator_name in cls._generator_classes:
            return cls._generator_classes[generator_name]
        
        if generator_name not in cls.MODULE_MAP:
            raise ValueError(f"Unknown generator: {generator_name}")
        
        module_path = cls.MODULE_MAP[generator_name]
        
        try:
            logger.debug(f"Lazy loading generator module: {module_path}")
            module = __import__(module_path, fromlist=[generator_name])
            generator_class = getattr(module, generator_name)
            
            # Cache the class
            cls._generator_classes[generator_name] = generator_class
            cls._loaded_modules[module_path] = True
            
            logger.info(f"Successfully loaded generator: {generator_name}")
            return generator_class
            
        except ImportError as e:
            logger.error(f"Failed to import generator module {module_path}: {e}")
            raise
        except AttributeError as e:
            logger.error(f"Generator class {generator_name} not found in module {module_path}: {e}")
            raise
    
    @classmethod
    def create_generator(
        cls,
        doc_type: str,
        input_file: Path,
        output_file: Path,
        **kwargs
    ) -> BaseGenerator:
        """
        Create appropriate generator instance based on document type.
        
        Args:
            doc_type: Type of document ('akazi_jobdesc', 'akazi_cv', 'mc2i_cv')
            input_file: Path to input JSON/YAML file
            output_file: Path to output DOCX file
            **kwargs: Additional generator-specific parameters
            
        Returns:
            Generator instance
            
        Raises:
            ValueError: If document type is not supported
            ImportError: If generator class cannot be loaded
        """
        if doc_type not in cls.GENERATOR_MAP:
            supported_types = ', '.join(cls.GENERATOR_MAP.keys())
            raise ValueError(
                f"Unsupported document type: {doc_type}. "
                f"Supported types: {supported_types}"
            )
        
        generator_name = cls.GENERATOR_MAP[doc_type]
        
        try:
            # Lazy load the generator class
            generator_class = cls._load_generator_class(generator_name)
            
            # Create and return generator instance
            logger.info(f"Creating {generator_name} instance for {input_file.name}")
            return generator_class(
                input_file=input_file,
                output_file=output_file,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Failed to create generator for type {doc_type}: {e}")
            raise
    
    @classmethod
    def detect_document_type(cls, input_file: Path) -> Optional[str]:
        """
        Auto-detect document type from JSON/YAML structure.
        
        Detection rules:
        - AKAZI Job Description: has 'header', 'sections', 'metadata.job_id'
        - AKAZI CV: has 'str_Initials', 'experiences', 'str_speciality'
        - MC2I CV: same as AKAZI CV (uses same structure)
        
        Args:
            input_file: Path to JSON/YAML file
            
        Returns:
            Detected document type or None if cannot detect
        """
        try:
            # Load the file
            with open(input_file, 'r', encoding='utf-8') as f:
                if input_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if not isinstance(data, dict):
                logger.warning(f"Invalid data structure in {input_file.name}")
                return None
            
            # Check for AKAZI Job Description
            if all(key in data for key in ['header', 'sections', 'metadata']):
                if 'job_id' in data.get('metadata', {}):
                    logger.info(f"Detected document type: akazi_jobdesc for {input_file.name}")
                    return 'akazi_jobdesc'
            
            # Check for CV structure (both AKAZI and MC2I use same JSON)
            if all(key in data for key in ['str_Initials', 'experiences', 'str_speciality']):
                # Default to AKAZI CV (user can override to MC2I via UI)
                logger.info(f"Detected CV structure for {input_file.name} (default: akazi_cv)")
                return 'akazi_cv'
            
            logger.warning(f"Could not detect document type for {input_file.name}")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting document type for {input_file.name}: {e}")
            return None
    
    @classmethod
    def validate_input_file(
        cls,
        input_file: Path,
        doc_type: str,
        validator: Optional[DocumentValidator] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate input file against schema for document type.
        FIXED: Loads data first, then validates the dictionary
        
        Args:
            input_file: Path to input file
            doc_type: Document type
            validator: Optional DocumentValidator instance (creates new if None)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if validator is None:
            validator = DocumentValidator()
        
        try:
            # Load the data first
            with open(input_file, 'r', encoding='utf-8') as f:
                if input_file.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            if not isinstance(data, dict):
                return False, "Data is not a dictionary"
            
            # Now validate the data dictionary
            is_valid, error_msg = validator.validate(data, doc_type, silent=True)
            
            if not is_valid:
                logger.error(f"Validation failed for {input_file.name}: {error_msg}")
            else:
                logger.debug(f"Validation passed for {input_file.name}")
            
            return is_valid, error_msg
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(f"Validation exception for {input_file.name}: {e}")
            return False, error_msg
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported document types."""
        return list(cls.GENERATOR_MAP.keys())
    
    @classmethod
    def get_loaded_generators(cls) -> list[str]:
        """Get list of currently loaded generator classes."""
        return list(cls._generator_classes.keys())
    
    @classmethod
    def clear_cache(cls):
        """Clear cached generator classes (useful for testing/debugging)."""
        cls._generator_classes.clear()
        cls._loaded_modules.clear()
        logger.info("Generator cache cleared")
