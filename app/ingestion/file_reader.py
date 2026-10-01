"""
File Reader Module
==================
Reads log files safely with support for different encodings and sizes.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class FileReader:
    """
    Safe file reader with encoding detection and size limits.
    """
    
    def __init__(self, max_file_size_mb: int = 500):
        self.max_file_size_mb = max_file_size_mb
        self.supported_extensions = ['.log', '.txt', '.csv', '.json', '.jsonl']
    
    def read_file(self, file_path: str) -> Tuple[str, dict]:
        """
        Read a log file and return content + metadata.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            Tuple of (file_content, metadata_dict)
        """
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in self.supported_extensions:
            logger.warning(f"Unsupported extension: {path.suffix}. Trying anyway...")
        
        # Check file size
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(
                f"File too large: {file_size_mb:.1f}MB > {self.max_file_size_mb}MB limit"
            )
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'ascii', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                logger.info(f"File read with {encoding} encoding")
                break
            except Exception as e:
                logger.debug(f"Failed with {encoding}: {e}")
                continue
        
        if content is None:
            raise ValueError("Could not read file with any supported encoding")
        
        # Metadata
        metadata = {
            'file_path': str(path.absolute()),
            'file_name': path.name,
            'file_size_mb': round(file_size_mb, 2),
            'file_extension': path.suffix,
            'encoding': encoding,
            'total_lines': content.count('\n') + 1,
            'total_chars': len(content)
        }
        
        logger.info(
            f"File loaded: {path.name} "
            f"({metadata['total_lines']} lines, "
            f"{metadata['file_size_mb']}MB)"
        )
        
        return content, metadata
    
    def read_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        """
        Read uploaded file content (from FastAPI UploadFile).
        
        Args:
            file_content: Raw bytes from uploaded file
            filename: Original filename
            
        Returns:
            Tuple of (decoded_content, metadata_dict)
        """
        # Check size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.1f}MB > {self.max_file_size_mb}MB limit"
            )
        
        # Try encodings
        encodings = ['utf-8', 'latin-1', 'ascii', 'cp1252']
        content = None
        
        for encoding in encodings:
            try:
                content = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            raise ValueError("Could not decode file content")
        
        metadata = {
            'file_name': filename,
            'file_size_mb': round(size_mb, 2),
            'encoding': encoding,
            'total_lines': content.count('\n') + 1,
            'total_chars': len(content)
        }
        
        return content, metadata
