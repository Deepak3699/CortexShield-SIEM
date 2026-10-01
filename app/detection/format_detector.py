"""
Format Detector Module
=====================
Detects the format of log files.
Supports: Apache, Nginx, IIS, JSON, JSONL, CSV, Custom
"""

import re
import json
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FormatResult:
    """Result of format detection."""
    format_name: str
    confidence: float  # 0.0 to 1.0
    is_known: bool
    parser_config: Optional[Dict] = None
    sample_analysis: Optional[Dict] = None


class FormatDetector:
    """
    Detects log file format from sample lines.
    
    Returns:
    - Known format (Apache, Nginx, etc.) → Predefined config
    - Unknown format → Needs AI assistance
    """
    
    # Known format patterns
    APACHE_COMBINED = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+) "(.*?)" "(.*?)"'
    )
    
    APACHE_CLF = re.compile(
        r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)'
    )
    
    NGINX_DEFAULT = re.compile(
        r'(\S+) - (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)"'
    )
    
    IP_PATTERN = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    METHOD_PATTERN = re.compile(r'\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b', re.IGNORECASE)
    STATUS_PATTERN = re.compile(r'\s([1-5]\d{2})\s')
    TIMESTAMP_BRACKET = re.compile(r'\[(.*?)\]')
    ISO_TIMESTAMP = re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}')
    
    def detect_format(self, sample_lines: List[str]) -> FormatResult:
        """
        Detect the format of log file from sample lines.
        
        Args:
            sample_lines: List of sample log lines
            
        Returns:
            FormatResult with detected format and config
        """
        if not sample_lines:
            raise ValueError("No sample lines provided")
        
        # Try each known format
        results = []
        
        # 1. Try Apache Combined
        score = self._test_apache_combined(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="apache_combined",
                confidence=score,
                is_known=True,
                parser_config=self._get_apache_combined_config()
            ))
        
        # 2. Try Apache CLF
        score = self._test_apache_clf(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="apache_clf",
                confidence=score,
                is_known=True,
                parser_config=self._get_apache_clf_config()
            ))
        
        # 3. Try Nginx
        score = self._test_nginx(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="nginx",
                confidence=score,
                is_known=True,
                parser_config=self._get_nginx_config()
            ))
        
        # 4. Try JSON
        score = self._test_json(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="json",
                confidence=score,
                is_known=True,
                parser_config=self._get_json_config()
            ))
        
        # 5. Try JSONL
        score = self._test_jsonl(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="jsonl",
                confidence=score,
                is_known=True,
                parser_config=self._get_jsonl_config()
            ))
        
        # 6. Try CSV
        score = self._test_csv(sample_lines)
        if score > 0.5:
            results.append(FormatResult(
                format_name="csv",
                confidence=score,
                is_known=True,
                parser_config=self._get_csv_config(sample_lines)
            ))
        
        # Return best match
        if results:
            best = max(results, key=lambda r: r.confidence)
            logger.info(f"Format detected: {best.format_name} (confidence: {best.confidence:.2f})")
            return best
        
        # Unknown format - needs AI
        logger.info("Unknown format - needs AI assistance")
        return FormatResult(
            format_name="unknown",
            confidence=0.0,
            is_known=False,
            sample_analysis=self._analyze_unknown_format(sample_lines)
        )
    
    def _test_apache_combined(self, lines: List[str]) -> float:
        """Test if lines match Apache Combined format."""
        matches = sum(1 for line in lines[:50] if self.APACHE_COMBINED.match(line.strip()))
        return matches / min(50, len(lines))
    
    def _test_apache_clf(self, lines: List[str]) -> float:
        """Test if lines match Apache CLF format."""
        matches = sum(1 for line in lines[:50] if self.APACHE_CLF.match(line.strip()))
        return matches / min(50, len(lines))
    
    def _test_nginx(self, lines: List[str]) -> float:
        """Test if lines match Nginx format."""
        matches = sum(1 for line in lines[:50] if self.NGINX_DEFAULT.match(line.strip()))
        return matches / min(50, len(lines))
    
    def _test_json(self, lines: List[str]) -> float:
        """Test if lines are JSON format."""
        json_count = 0
        for line in lines[:20]:
            line = line.strip()
            if line.startswith('{'):
                try:
                    json.loads(line)
                    json_count += 1
                except json.JSONDecodeError:
                    pass
        return json_count / min(20, len(lines))
    
    def _test_jsonl(self, lines: List[str]) -> float:
        """Test if lines are JSONL format."""
        return self._test_json(lines)  # Same test
    
    def _test_csv(self, lines: List[str]) -> float:
        """Test if lines are CSV format."""
        if not lines:
            return 0.0
        
        # Check if lines have consistent number of commas/tabs
        delimiters = [',', '\t', '|']
        
        for delim in delimiters:
            counts = [line.count(delim) for line in lines[:20] if line.strip()]
            if counts and len(set(counts)) == 1 and counts[0] >= 2:
                return 0.8
        
        return 0.0
    
    def _analyze_unknown_format(self, lines: List[str]) -> Dict:
        """
        Analyze unknown format to help AI understand it.
        """
        analysis = {
            'total_sample_lines': len(lines),
            'has_ip': False,
            'has_timestamp': False,
            'has_method': False,
            'has_status': False,
            'has_url': False,
            'possible_delimiter': None,
            'line_lengths': [],
            'first_5_lines': lines[:5]
        }
        
        for line in lines[:50]:
            if self.IP_PATTERN.search(line):
                analysis['has_ip'] = True
            if self.TIMESTAMP_BRACKET.search(line) or self.ISO_TIMESTAMP.search(line):
                analysis['has_timestamp'] = True
            if self.METHOD_PATTERN.search(line):
                analysis['has_method'] = True
            if self.STATUS_PATTERN.search(line):
                analysis['has_status'] = True
            if '/' in line and ('http' in line.lower() or self.METHOD_PATTERN.search(line)):
                analysis['has_url'] = True
            analysis['line_lengths'].append(len(line))
        
        # Detect delimiter
        for line in lines[:10]:
            for delim in [',', '\t', '|', ';']:
                if delim in line:
                    analysis['possible_delimiter'] = delim
                    break
        
        return analysis
    
    def _get_apache_combined_config(self) -> Dict:
        """Get parser config for Apache Combined format."""
        return {
            'format': 'apache_combined',
            'regex': r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+) "(.*?)" "(.*?)"',
            'fields': ['ip', 'ident', 'authuser', 'timestamp', 'request', 'status', 'bytes', 'referer', 'user_agent'],
            'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
            'request_split': True  # Split "GET /url HTTP/1.1"
        }
    
    def _get_apache_clf_config(self) -> Dict:
        """Get parser config for Apache CLF format."""
        return {
            'format': 'apache_clf',
            'regex': r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+)',
            'fields': ['ip', 'ident', 'authuser', 'timestamp', 'request', 'status', 'bytes'],
            'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
            'request_split': True
        }
    
    def _get_nginx_config(self) -> Dict:
        """Get parser config for Nginx format."""
        return {
            'format': 'nginx',
            'regex': r'(\S+) - (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)"',
            'fields': ['ip', 'ident', 'timestamp', 'request', 'status', 'bytes', 'referer', 'user_agent'],
            'timestamp_format': '%d/%b/%Y:%H:%M:%S %z',
            'request_split': True
        }
    
    def _get_json_config(self) -> Dict:
        """Get parser config for JSON format."""
        return {
            'format': 'json',
            'type': 'json',
            'field_mapping': {
                'ip': ['ip', 'client_ip', 'remote_addr', 'client_ip_address'],
                'timestamp': ['timestamp', 'time', 'datetime', '@timestamp'],
                'method': ['method', 'http_method', 'request_method'],
                'url': ['url', 'path', 'request_uri', 'uri'],
                'status': ['status', 'status_code', 'response_status'],
                'bytes': ['bytes', 'body_bytes_sent', 'response_size'],
                'user_agent': ['user_agent', 'agent', 'http_user_agent']
            }
        }
    
    def _get_jsonl_config(self) -> Dict:
        """Get parser config for JSONL format."""
        return self._get_json_config()  # Same config
    
    def _get_csv_config(self, lines: List[str]) -> Dict:
        """Get parser config for CSV format."""
        # Try to detect header
        first_line = lines[0].strip() if lines else ''
        
        # Detect delimiter
        delimiter = ','
        for d in ['\t', '|', ';']:
            if d in first_line:
                delimiter = d
                break
        
        # Try to parse header
        headers = [h.strip().lower() for h in first_line.split(delimiter)]
        
        return {
            'format': 'csv',
            'type': 'csv',
            'delimiter': delimiter,
            'has_header': self._looks_like_header(headers),
            'headers': headers if self._looks_like_header(headers) else None
        }
    
    def _looks_like_header(self, fields: List[str]) -> bool:
        """Check if fields look like a CSV header."""
        header_keywords = ['ip', 'time', 'date', 'method', 'url', 'status', 'size', 'agent']
        matches = sum(1 for f in fields if any(kw in f for kw in header_keywords))
        return matches >= 2
