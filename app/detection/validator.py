"""
Validator Module
================
Validates parser configurations - never blindly trust AI!
"""

import re
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Validator:
    """
    Validates parser configurations against sample data.
    
    IMPORTANT: Never blindly trust AI output!
    Always validate before using.
    """
    
    # Apache CLF logs can have hostnames (e.g. unicomp6.unicomp.net) instead of numeric IPs
    IP_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    HOSTNAME_PATTERN = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]{0,253}[a-zA-Z0-9])?$')
    VALID_METHODS = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}
    
    def validate_config(self, config: Dict, sample_lines: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate a parser configuration against sample lines.
        
        Args:
            config: Parser configuration dict
            sample_lines: Sample lines to test against
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Test parsing with config
        parsed_count = 0
        total_count = min(50, len(sample_lines))
        
        for line in sample_lines[:total_count]:
            try:
                result = self._parse_line(line, config)
                if result:
                    # Validate parsed fields
                    line_errors = self._validate_parsed_fields(result)
                    if line_errors:
                        errors.extend(line_errors)
                    else:
                        parsed_count += 1
            except Exception as e:
                errors.append(f"Parse error: {str(e)[:50]}")
        
        # Check success rate
        success_rate = parsed_count / total_count if total_count > 0 else 0
        
        if success_rate < 0.5:
            errors.append(f"Low success rate: {success_rate:.1%} < 50%")
        
        is_valid = len(errors) == 0 and success_rate >= 0.5
        
        if is_valid:
            logger.info(f"Validation PASSED: {success_rate:.1%} success rate")
        else:
            logger.warning(f"Validation FAILED: {len(errors)} errors, {success_rate:.1%} success")
        
        return is_valid, errors
    
    def _parse_line(self, line: str, config: Dict) -> Dict:
        """Parse a single line using config."""
        line = line.strip()
        if not line:
            return None
        
        format_type = config.get('format', '')
        
        if format_type in ['apache_combined', 'apache_clf', 'nginx']:
            return self._parse_regex_line(line, config)
        elif format_type == 'json':
            return self._parse_json_line(line, config)
        elif format_type == 'csv':
            return self._parse_csv_line(line, config)
        
        return None
    
    def _parse_regex_line(self, line: str, config: Dict) -> Dict:
        """Parse line using regex."""
        pattern = config.get('regex')
        fields = config.get('fields', [])
        
        if not pattern or not fields:
            return None
        
        match = re.match(pattern, line)
        if not match:
            return None
        
        groups = match.groups()
        result = {}
        
        for i, field in enumerate(fields):
            if i < len(groups):
                result[field] = groups[i]
        
        # Split request if needed
        if config.get('request_split') and 'request' in result:
            parts = result['request'].split()
            if len(parts) >= 2:
                result['method'] = parts[0]
                result['url'] = parts[1]
            if len(parts) >= 3:
                result['protocol'] = parts[2]
        
        return result
    
    def _parse_json_line(self, line: str, config: Dict) -> Dict:
        """Parse JSON line."""
        import json
        try:
            data = json.loads(line)
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    
    def _parse_csv_line(self, line: str, config: Dict) -> Dict:
        """Parse CSV line."""
        delimiter = config.get('delimiter', ',')
        headers = config.get('headers')
        
        fields = line.split(delimiter)
        
        if headers and len(fields) == len(headers):
            return dict(zip(headers, fields))
        
        return None
    
    def _validate_parsed_fields(self, parsed: Dict) -> List[str]:
        """Validate individual parsed fields."""
        errors = []
        
        # Validate IP (can be numeric IPv4 or a hostname in Apache CLF logs)
        if 'ip' in parsed:
            ip = parsed['ip']
            if ip and ip not in ('0.0.0.0', '-'):
                is_numeric_ip = self.IP_PATTERN.match(ip)
                is_hostname = self.HOSTNAME_PATTERN.match(ip)
                if not is_numeric_ip and not is_hostname:
                    errors.append(f"Invalid IP: {ip}")
        
        # Validate status
        if 'status' in parsed:
            try:
                status = int(parsed['status'])
                if not (100 <= status <= 599):
                    errors.append(f"Invalid status: {status}")
            except (ValueError, TypeError):
                errors.append(f"Status not a number: {parsed['status']}")
        
        # Validate method
        if 'method' in parsed:
            method = str(parsed['method']).upper()
            if method not in self.VALID_METHODS and method != 'UNKNOWN':
                errors.append(f"Invalid method: {method}")
        
        return errors
