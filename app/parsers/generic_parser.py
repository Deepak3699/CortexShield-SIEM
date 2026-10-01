"""
Generic Parser Module
=====================
Parses log files using a configuration.
Works with any format once config is validated.
"""

import re
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dateutil import parser as date_parser
import pandas as pd

logger = logging.getLogger(__name__)


class GenericParser:
    """
    Generic log parser that works with any format.
    
    Once we have a validated config, this parser can process
    ANY size file (5GB, 10GB, 100GB) without sending to AI.
    """
    
    def __init__(self):
        self.stats = {
            'total_lines': 0,
            'parsed_lines': 0,
            'failed_lines': 0
        }
    
    def parse(self, content: str, config: Dict) -> pd.DataFrame:
        """
        Parse entire file using config.
        
        Args:
            content: Full file content
            config: Validated parser configuration
            
        Returns:
            DataFrame with parsed events
        """
        format_type = config.get('format', '')
        
        logger.info(f"Parsing with config: {format_type}")
        
        if format_type in ['apache_combined', 'apache_clf', 'nginx']:
            return self._parse_regex(content, config)
        elif format_type == 'json':
            return self._parse_json(content, config)
        elif format_type == 'jsonl':
            return self._parse_jsonl(content, config)
        elif format_type == 'csv':
            return self._parse_csv(content, config)
        elif 'delimited' in format_type:
            return self._parse_delimited(content, config)
        else:
            raise ValueError(f"Unknown format: {format_type}")
    
    def _parse_regex(self, content: str, config: Dict) -> pd.DataFrame:
        """Parse regex-based formats (Apache, Nginx, etc.)."""
        pattern = re.compile(config['regex'])
        fields = config['fields']
        request_split = config.get('request_split', False)
        
        rows = []
        failed = 0
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            match = pattern.match(line)
            if match:
                groups = match.groups()
                row = {}
                
                for i, field in enumerate(fields):
                    if i < len(groups):
                        row[field] = groups[i]
                
                # Split request if needed
                if request_split and 'request' in row:
                    parts = row['request'].split()
                    if len(parts) >= 2:
                        row['method'] = parts[0]
                        row['url'] = parts[1]
                    if len(parts) >= 3:
                        row['protocol'] = parts[2]
                
                rows.append(row)
            else:
                failed += 1
        
        self.stats['total_lines'] = len(rows) + failed
        self.stats['parsed_lines'] = len(rows)
        self.stats['failed_lines'] = failed
        
        logger.info(f"Parsed {len(rows)} lines, {failed} failed")
        
        df = pd.DataFrame(rows)
        return self._clean_dataframe(df, config)
    
    def _parse_json(self, content: str, config: Dict) -> pd.DataFrame:
        """Parse JSON format."""
        mapping = config.get('field_mapping', {})
        
        rows = []
        failed = 0
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if isinstance(data, dict):
                    row = self._map_json_fields(data, mapping)
                    rows.append(row)
                else:
                    failed += 1
            except json.JSONDecodeError:
                failed += 1
        
        self.stats['total_lines'] = len(rows) + failed
        self.stats['parsed_lines'] = len(rows)
        self.stats['failed_lines'] = failed
        
        df = pd.DataFrame(rows)
        return self._clean_dataframe(df, config)
    
    def _parse_jsonl(self, content: str, config: Dict) -> pd.DataFrame:
        """Parse JSONL format (same as JSON)."""
        return self._parse_json(content, config)
    
    def _parse_csv(self, content: str, config: Dict) -> pd.DataFrame:
        """Parse CSV format."""
        delimiter = config.get('delimiter', ',')
        has_header = config.get('has_header', True)
        headers = config.get('headers')
        
        try:
            if has_header:
                df = pd.read_csv(
                    pd.io.common.StringIO(content),
                    delimiter=delimiter
                )
            else:
                df = pd.read_csv(
                    pd.io.common.StringIO(content),
                    delimiter=delimiter,
                    header=None,
                    names=headers
                )
            
            self.stats['total_lines'] = len(df)
            self.stats['parsed_lines'] = len(df)
            self.stats['failed_lines'] = 0
            
            return self._clean_dataframe(df, config)
            
        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            raise
    
    def _parse_delimited(self, content: str, config: Dict) -> pd.DataFrame:
        """Parse custom delimited format."""
        delimiter = config.get('delimiter', ' ')
        fields = config.get('fields', [])
        
        rows = []
        failed = 0
        
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(delimiter)
            
            if len(parts) >= len(fields):
                row = {}
                for i, field in enumerate(fields):
                    if i < len(parts):
                        row[field] = parts[i].strip()
                rows.append(row)
            else:
                failed += 1
        
        self.stats['total_lines'] = len(rows) + failed
        self.stats['parsed_lines'] = len(rows)
        self.stats['failed_lines'] = failed
        
        df = pd.DataFrame(rows)
        return self._clean_dataframe(df, config)
    
    def _map_json_fields(self, data: Dict, mapping: Dict) -> Dict:
        """Map JSON fields to standard names."""
        result = {}
        
        for standard_name, possible_names in mapping.items():
            for name in possible_names:
                if name in data:
                    result[standard_name] = data[name]
                    break
        
        return result
    
    def _clean_dataframe(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Clean and prepare DataFrame."""
        if df.empty:
            return df
        
        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = df['timestamp'].apply(self._parse_timestamp)
            df = df.dropna(subset=['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # Parse status
        if 'status' in df.columns:
            df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0).astype(int)
        
        # Parse bytes
        if 'bytes' in df.columns:
            df['bytes'] = df['bytes'].replace('-', '0')
            df['bytes'] = pd.to_numeric(df['bytes'], errors='coerce').fillna(0).astype(int)
        
        # Clean method
        if 'method' in df.columns:
            df['method'] = df['method'].str.upper()
        
        logger.info(f"Cleaned DataFrame: {len(df)} rows, {len(df.columns)} columns")
        
        return df
    
    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        """Parse timestamp with multiple format support."""
        if pd.isna(value) or not value:
            return None
        
        value = str(value).strip('[]')
        
        formats = [
            '%d/%b/%Y:%H:%M:%S %z',
            '%d/%b/%Y:%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        try:
            return date_parser.parse(value)
        except Exception:
            return None
    
    def get_stats(self) -> Dict:
        """Get parsing statistics."""
        return self.stats.copy()
