"""
File Handler Module
Handles file uploads, downloads, and format conversions (JSON/YAML)
"""

import json
import yaml
from io import BytesIO, StringIO
from typing import List, Dict, Union, Optional, BinaryIO
from pathlib import Path
import streamlit as st

from utils.logger import logger


class FileHandler:
    """Handle file operations for JSON and YAML formats"""
    
    SUPPORTED_EXTENSIONS = ['.json', '.yaml', '.yml']
    
    @staticmethod
    def load_file(
        file: Union[BinaryIO, str, Path],
        encoding: str = 'utf-8'
    ) -> Dict:
        """
        Load JSON or YAML file
        
        Args:
            file: File object, path string, or Path object
            encoding: File encoding
        
        Returns:
            Parsed data dictionary
        
        Raises:
            ValueError: If file format is not supported
            json.JSONDecodeError: If JSON is malformed
            yaml.YAMLError: If YAML is malformed
        """
        # Determine file type
        if hasattr(file, 'name'):
            filename = file.name
        elif isinstance(file, (str, Path)):
            filename = str(file)
        else:
            raise ValueError("File must have a name attribute or be a path")
        
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in FileHandler.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(FileHandler.SUPPORTED_EXTENSIONS)}"
            )
        
        # Read file content
        try:
            if hasattr(file, 'read'):
                # File-like object (e.g., UploadedFile)
                content = file.read()
                if isinstance(content, bytes):
                    content = content.decode(encoding)
            else:
                # Path
                with open(file, 'r', encoding=encoding) as f:
                    content = f.read()
        except Exception as e:
            logger.error("file_read_failed", filename=filename, error=str(e))
            raise IOError(f"Failed to read file: {str(e)}") from e
        
        # Parse content
        try:
            if file_ext == '.json':
                data = json.loads(content)
                logger.info("json_file_loaded", filename=filename)
            else:  # .yaml or .yml
                data = yaml.safe_load(content)
                logger.info("yaml_file_loaded", filename=filename)
            
            return data
        
        except json.JSONDecodeError as e:
            logger.error("json_parse_error", filename=filename, error=str(e))
            raise
        except yaml.YAMLError as e:
            logger.error("yaml_parse_error", filename=filename, error=str(e))
            raise
    
    @staticmethod
    def load_multiple_files(
        files: List[Union[BinaryIO, str, Path]]
    ) -> List[Dict]:
        """
        Load multiple JSON/YAML files
        
        Args:
            files: List of file objects or paths
        
        Returns:
            List of parsed data dictionaries
        """
        results = []
        
        for file in files:
            try:
                data = FileHandler.load_file(file)
                results.append(data)
            except Exception as e:
                filename = getattr(file, 'name', str(file))
                logger.error("batch_load_file_failed", filename=filename, error=str(e))
                # Re-raise to handle at higher level
                raise
        
        return results
    
    @staticmethod
    def save_to_json(
        data: Dict,
        output_path: Union[str, Path],
        indent: int = 2
    ):
        """
        Save data to JSON file
        
        Args:
            data: Data to save
            output_path: Output file path
            indent: JSON indentation level
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            logger.info("json_file_saved", path=str(output_path))
        
        except Exception as e:
            logger.error("json_save_failed", path=str(output_path), error=str(e))
            raise
    
    @staticmethod
    def save_to_yaml(
        data: Dict,
        output_path: Union[str, Path]
    ):
        """
        Save data to YAML file
        
        Args:
            data: Data to save
            output_path: Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    data,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False
                )
            
            logger.info("yaml_file_saved", path=str(output_path))
        
        except Exception as e:
            logger.error("yaml_save_failed", path=str(output_path), error=str(e))
            raise
    
    @staticmethod
    def get_file_size_kb(file: Union[BinaryIO, str, Path]) -> float:
        """
        Get file size in kilobytes
        
        Args:
            file: File object or path
        
        Returns:
            File size in KB
        """
        try:
            if hasattr(file, 'size'):
                # Streamlit UploadedFile
                return file.size / 1024
            elif hasattr(file, 'seek') and hasattr(file, 'tell'):
                # File-like object
                current_pos = file.tell()
                file.seek(0, 2)  # Seek to end
                size = file.tell()
                file.seek(current_pos)  # Restore position
                return size / 1024
            else:
                # Path
                return Path(file).stat().st_size / 1024
        except Exception:
            return 0.0
    
    @staticmethod
    def create_download_link(
        content: bytes,
        filename: str,
        label: str = "Download"
    ) -> str:
        """
        Create a download link for Streamlit
        
        Args:
            content: File content as bytes
            filename: Download filename
            label: Button label
        
        Returns:
            Streamlit download button component
        """
        # Note: This returns the button, not HTML
        # Used with st.download_button()
        return {
            "data": content,
            "file_name": filename,
            "label": label
        }
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate and sanitize filename
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        sanitized = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # Ensure it has an extension
        if '.' not in sanitized:
            sanitized += '.json'
        
        return sanitized


class StreamlitFileUploader:
    """Helper class for Streamlit file upload operations"""
    
    @staticmethod
    def upload_files(
        label: str = "Upload JSON/YAML files",
        accept_multiple: bool = True,
        key: Optional[str] = None
    ) -> Optional[Union[List[BinaryIO], BinaryIO]]:
        """
        Create Streamlit file uploader
        
        Args:
            label: Uploader label
            accept_multiple: Allow multiple files
            key: Streamlit widget key
        
        Returns:
            Uploaded file(s) or None
        """
        return st.file_uploader(
            label,
            type=['json', 'yaml', 'yml'],
            accept_multiple_files=accept_multiple,
            key=key,
            help="Upload JSON or YAML files containing document data"
        )
    
    @staticmethod
    def process_uploaded_files(
        uploaded_files: Union[List[BinaryIO], BinaryIO]
    ) -> List[Dict]:
        """
        Process uploaded files and return parsed data
        
        Args:
            uploaded_files: File(s) from st.file_uploader
        
        Returns:
            List of parsed data dictionaries with metadata
        """
        if not uploaded_files:
            return []
        
        # Ensure it's a list
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        results = []
        
        for file in uploaded_files:
            try:
                # Get file size
                file_size_kb = FileHandler.get_file_size_kb(file)
                
                # Parse file
                data = FileHandler.load_file(file)
                
                results.append({
                    "filename": file.name,
                    "size_kb": round(file_size_kb, 2),
                    "data": data,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "filename": file.name,
                    "size_kb": 0,
                    "data": None,
                    "error": str(e)
                })
        
        return results
