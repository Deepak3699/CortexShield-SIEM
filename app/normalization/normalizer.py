"""
Normalizer Module
=================
Converts parsed data from any format into the common schema.
"""

import logging
from typing import Dict, List
import pandas as pd

from .schema import NormalizedEvent, STANDARD_FIELDS, FIELD_ALIASES

logger = logging.getLogger(__name__)


class Normalizer:
    """
    Converts parsed data into normalized events.
    
    This is the FOUNDATION of the system.
    After normalization, all downstream code (analytics, security, ML)
    works the same way regardless of original format.
    """
    
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a DataFrame to common schema.
        
        Args:
            df: Parsed DataFrame (may have different column names)
            
        Returns:
            Normalized DataFrame with standard column names
        """
        logger.info(f"Normalizing DataFrame: {len(df)} rows, columns: {list(df.columns)}")
        
        # Map field names to standard names
        normalized = self._map_fields(df)
        
        # Ensure all standard fields exist
        normalized = self._ensure_fields(normalized)
        
        # Clean and validate
        normalized = self._clean(normalized)
        
        # Add derived fields
        normalized = self._add_derived(normalized)
        
        logger.info(f"Normalized: {len(normalized)} rows, columns: {list(normalized.columns)}")
        
        return normalized
    
    def _map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map field aliases to standard names."""
        result = df.copy()
        
        for standard_name, aliases in FIELD_ALIASES.items():
            if standard_name not in result.columns:
                for alias in aliases:
                    if alias in result.columns:
                        result = result.rename(columns={alias: standard_name})
                        logger.debug(f"Mapped {alias} -> {standard_name}")
                        break
        
        return result
    
    def _ensure_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all standard fields exist with defaults."""
        result = df.copy()
        
        defaults = {
            'timestamp': None,
            'ip': '0.0.0.0',
            'method': 'UNKNOWN',
            'url': '/',
            'protocol': 'HTTP/1.0',
            'status': 0,
            'bytes': 0,
            'user_agent': None,
            'referer': None
        }
        
        for field, default in defaults.items():
            if field not in result.columns:
                result[field] = default
                logger.debug(f"Added missing field: {field} = {default}")
        
        return result
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate fields."""
        result = df.copy()
        
        # Clean IP
        if 'ip' in result.columns:
            result['ip'] = result['ip'].fillna('0.0.0.0')
        
        # Clean method
        if 'method' in result.columns:
            result['method'] = result['method'].fillna('UNKNOWN').str.upper()
        
        # Clean URL
        if 'url' in result.columns:
            result['url'] = result['url'].fillna('/')
        
        # Clean status
        if 'status' in result.columns:
            result['status'] = pd.to_numeric(result['status'], errors='coerce').fillna(0).astype(int)
        
        # Clean bytes
        if 'bytes' in result.columns:
            result['bytes'] = result['bytes'].replace('-', '0')
            result['bytes'] = pd.to_numeric(result['bytes'], errors='coerce').fillna(0).astype(int)
        
        return result
    
    def _add_derived(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived fields."""
        result = df.copy()
        
        # Time-based fields
        if 'timestamp' in result.columns and pd.api.types.is_datetime64_any_dtype(result['timestamp']):
            result['hour'] = result['timestamp'].dt.hour
            result['day'] = result['timestamp'].dt.day
            result['month'] = result['timestamp'].dt.month
            result['day_of_week'] = result['timestamp'].dt.dayofweek
            result['is_weekend'] = (result['day_of_week'] >= 5).astype(int)
        
        # Error flag
        if 'status' in result.columns:
            result['is_error'] = (result['status'] >= 400).astype(int)
        
        return result
