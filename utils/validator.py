"""
Document Validator Module
Validates JSON/YAML data against schemas and auto-detects document type
FIXED VERSION - Uses correct schema paths and format detection
"""

import jsonschema
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import json

from utils.logger import logger


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DocumentValidator:
    """
    Validates document structure and auto-detects document type
    Uses REAL schemas based on actual AI output format
    """
    
    # Schema directory
    SCHEMA_DIR = Path("schemas")
    
    # Schema mapping - maps doc type to schema filename
    SCHEMA_MAP = {
        "akazi_jobdesc": "akazi_jobdesc_schema.json",
        "cv_source": "cv_source_format.json",  # REAL format from AI
        "mc2i_cv": "mc2i_cv_schema.json"  # Can use same source format
    }
    
    # Detection signatures for each document type
    DETECTION_SIGNATURES = {
        "akazi_jobdesc": {
            "required_keys": ["metadata", "header", "sections"],
            "nested_checks": [
                ("metadata", "job_id"),
                ("header", "title"),
                ("sections", "global_mission")
            ]
        },
        "cv_source": {
            "required_keys": ["str_Initials", "str_speciality", "experiences"],
            "nested_checks": []
        }
    }
    
    # Cache for loaded schemas
    _schema_cache: Dict[str, Dict] = {}
    
    @classmethod
    def load_schema(cls, schema_name: str) -> Dict:
        """
        Load JSON schema from file with caching
        
        Args:
            schema_name: Name of schema file
            
        Returns:
            Loaded schema dictionary
        """
        if schema_name in cls._schema_cache:
            return cls._schema_cache[schema_name]
        
        schema_path = cls.SCHEMA_DIR / schema_name
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            cls._schema_cache[schema_name] = schema
            logger.info("schema_loaded", schema_name=schema_name)
            return schema
            
        except json.JSONDecodeError as e:
            logger.error("schema_parse_error", schema_name=schema_name, error=str(e))
            raise
    
    @classmethod
    def detect_type(cls, data: Dict) -> Optional[str]:
        """
        Auto-detect document type from data structure
        
        Args:
            data: JSON/YAML data dictionary
        
        Returns:
            Document type string or None if unrecognized
        """
        if not isinstance(data, dict):
            logger.warning("validation_type_detection_failed", reason="Data is not a dictionary")
            return None
        
        # Try each document type
        for doc_type, signature in cls.DETECTION_SIGNATURES.items():
            if cls._matches_signature(data, signature):
                logger.info("document_type_detected", doc_type=doc_type)
                return doc_type
        
        logger.warning("document_type_unknown", available_keys=list(data.keys()))
        return None
    
    @classmethod
    def _matches_signature(cls, data: Dict, signature: Dict) -> bool:
        """
        Check if data matches a document type signature
        
        Args:
            data: Data dictionary
            signature: Signature dictionary with required/optional keys
        
        Returns:
            True if matches, False otherwise
        """
        # Check required keys
        required = signature.get("required_keys", [])
        if not all(key in data for key in required):
            return False
        
        # Check nested structures
        nested_checks = signature.get("nested_checks", [])
        for parent_key, child_key in nested_checks:
            if parent_key in data:
                if not isinstance(data[parent_key], dict):
                    return False
                if child_key not in data[parent_key]:
                    return False
        
        return True
    
    @classmethod
    def validate(
        cls,
        data: Dict,
        doc_type: Optional[str] = None,
        silent: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            doc_type: Document type (auto-detected if None)
            silent: If True, don't raise exceptions
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Auto-detect type if not provided
        if doc_type is None:
            doc_type = cls.detect_type(data)
            if doc_type is None:
                error_msg = "Could not auto-detect document type"
                if not silent:
                    raise ValidationError(error_msg)
                return False, error_msg
        
        # Special handling: akazi_cv and mc2i_cv both use cv_source format
        if doc_type in ["akazi_cv", "mc2i_cv"]:
            doc_type = "cv_source"
        
        # Load schema
        try:
            schema_filename = cls.SCHEMA_MAP.get(doc_type)
            if not schema_filename:
                error_msg = f"Unknown document type: {doc_type}"
                if not silent:
                    raise ValidationError(error_msg)
                return False, error_msg
            
            schema = cls.load_schema(schema_filename)
        
        except Exception as e:
            error_msg = f"Failed to load schema: {str(e)}"
            logger.error("schema_load_failed", doc_type=doc_type, error=str(e))
            if not silent:
                raise ValidationError(error_msg) from e
            return False, error_msg
        
        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=schema)
            logger.info("validation_success", doc_type=doc_type)
            return True, None
        
        except jsonschema.ValidationError as e:
            error_msg = cls._format_validation_error(e)
            logger.error(
                "validation_failed",
                doc_type=doc_type,
                error=error_msg,
                path=list(e.path)
            )
            
            if not silent:
                raise ValidationError(error_msg) from e
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected validation error: {str(e)}"
            logger.error("validation_unexpected_error", error=str(e))
            if not silent:
                raise ValidationError(error_msg) from e
            return False, error_msg
    
    @staticmethod
    def _format_validation_error(error: jsonschema.ValidationError) -> str:
        """
        Format validation error for user-friendly display
        
        Args:
            error: JSONSchema validation error
        
        Returns:
            Formatted error message
        """
        path = " → ".join(str(p) for p in error.path) if error.path else "root"
        
        return (
            f"Validation error at '{path}': {error.message}\n"
            f"Schema rule: {error.validator} = {error.validator_value}"
        )
    
    @classmethod
    def get_compatible_formats(cls, doc_type: str) -> List[str]:
        """
        Get list of compatible output formats for a document type
        
        Args:
            doc_type: Document type
        
        Returns:
            List of compatible format identifiers
        """
        compatibility_map = {
            "akazi_jobdesc": ["akazi_jobdesc_en", "akazi_jobdesc_fr"],
            "cv_source": ["akazi_cv", "mc2i_cv"],
            "akazi_cv": ["akazi_cv"],
            "mc2i_cv": ["mc2i_cv"]
        }
        
        formats = compatibility_map.get(doc_type, [])
        logger.debug("compatible_formats_retrieved", doc_type=doc_type, formats=formats)
        return formats
    
    @classmethod
    def validate_batch(
        cls,
        data_list: List[Dict],
        silent: bool = True
    ) -> List[Dict]:
        """
        Validate multiple documents
        
        Args:
            data_list: List of data dictionaries
            silent: If True, continue on errors
        
        Returns:
            List of validation results with structure:
            {
                "index": int,
                "valid": bool,
                "doc_type": str or None,
                "error": str or None
            }
        """
        results = []
        
        for idx, data in enumerate(data_list):
            doc_type = cls.detect_type(data)
            is_valid, error = cls.validate(data, doc_type, silent=True)
            
            results.append({
                "index": idx,
                "valid": is_valid,
                "doc_type": doc_type,
                "error": error
            })
        
        return results
