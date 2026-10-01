"""
Security Rules Module
=====================
Rule-based security detection - NOT ML!
"""

import re
import logging
from typing import Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class SecurityRules:
    """
    Rule-based security detection.
    
    This is NORMAL PYTHON with REGEX - not ML!
    """
    
    # SQL Injection patterns
    SQL_PATTERNS = re.compile(
        r"('|--|union|select|insert|update|delete|drop|alter|create|exec|execute|"
        r"or\s+1\s*=\s*1|or\s+'1'\s*=\s*'|waitfor|delay|benchmark|sleep)",
        re.IGNORECASE
    )
    
    # XSS patterns
    XSS_PATTERNS = re.compile(
        r"(<script|javascript:|onerror=|onload=|onclick=|onmouseover=|"
        r"<iframe|<object|<embed|alert\(|confirm\(|prompt\()",
        re.IGNORECASE
    )
    
    # Path Traversal patterns
    PATH_TRAVERSAL = re.compile(
        r'(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|%2e%2e%5c)',
        re.IGNORECASE
    )
    
    # Scanner patterns
    SCANNER_PATHS = re.compile(
        r'(/admin|/\.env|/config|/backup|/phpMyAdmin|/wp-admin|/wp-login|'
        r'/cgi-bin|/shell|/cmd|/exec|/test|/debug|/console)',
        re.IGNORECASE
    )
    
    def detect_threats(self, df: pd.DataFrame) -> Dict:
        """
        Detect security threats using rules.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            Dict with detected threats
        """
        logger.info(f"Running security rules on {len(df)} events")
        
        threats = {
            'sql_injection': self._detect_sql(df),
            'xss': self._detect_xss(df),
            'path_traversal': self._detect_path_traversal(df),
            'brute_force': self._detect_brute_force(df),
            'scanners': self._detect_scanners(df),
            'suspicious_ips': self._detect_suspicious_ips(df)
        }
        
        # Summary
        total_threats = sum(len(v) if isinstance(v, list) else 0 for v in threats.values())
        threats['total_threats'] = total_threats
        
        logger.info(f"Detected {total_threats} threats")
        
        return threats
    
    def _detect_sql(self, df: pd.DataFrame) -> List[Dict]:
        """Detect SQL injection attempts."""
        if 'url' not in df.columns:
            return []
        
        sql_attempts = df[df['url'].str.contains(self.SQL_PATTERNS, regex=True, na=False)]
        
        return [
            {
                'ip': row.get('ip', 'unknown'),
                'url': row.get('url', ''),
                'timestamp': str(row.get('timestamp', '')),
                'type': 'sql_injection'
            }
            for _, row in sql_attempts.head(50).iterrows()
        ]
    
    def _detect_xss(self, df: pd.DataFrame) -> List[Dict]:
        """Detect XSS attempts."""
        if 'url' not in df.columns:
            return []
        
        xss_attempts = df[df['url'].str.contains(self.XSS_PATTERNS, regex=True, na=False)]
        
        return [
            {
                'ip': row.get('ip', 'unknown'),
                'url': row.get('url', ''),
                'timestamp': str(row.get('timestamp', '')),
                'type': 'xss'
            }
            for _, row in xss_attempts.head(50).iterrows()
        ]
    
    def _detect_path_traversal(self, df: pd.DataFrame) -> List[Dict]:
        """Detect path traversal attempts."""
        if 'url' not in df.columns:
            return []
        
        traversal = df[df['url'].str.contains(self.PATH_TRAVERSAL, regex=True, na=False)]
        
        return [
            {
                'ip': row.get('ip', 'unknown'),
                'url': row.get('url', ''),
                'timestamp': str(row.get('timestamp', '')),
                'type': 'path_traversal'
            }
            for _, row in traversal.head(50).iterrows()
        ]
    
    def _detect_brute_force(self, df: pd.DataFrame) -> List[Dict]:
        """Detect brute force attempts."""
        if 'ip' not in df.columns or 'status' not in df.columns:
            return []
        
        # Find IPs with many 401/403 responses
        failed_logins = df[df['status'].isin([401, 403])]
        
        if failed_logins.empty:
            return []
        
        ip_failures = failed_logins.groupby('ip').size()
        suspicious = ip_failures[ip_failures > 10]  # More than 10 failures
        
        return [
            {
                'ip': ip,
                'failed_attempts': int(count),
                'type': 'brute_force'
            }
            for ip, count in suspicious.items()
        ]
    
    def _detect_scanners(self, df: pd.DataFrame) -> List[Dict]:
        """Detect vulnerability scanners."""
        if 'url' not in df.columns:
            return []
        
        scanner_attempts = df[df['url'].str.contains(self.SCANNER_PATHS, regex=True, na=False)]
        
        # Group by IP
        scanner_ips = scanner_attempts.groupby('ip').agg({
            'url': lambda x: list(x.unique()),
            'timestamp': 'count'
        }).rename(columns={'timestamp': 'attempt_count'})
        
        return [
            {
                'ip': ip,
                'attempt_count': int(row['attempt_count']),
                'urls': row['url'][:10],  # First 10 URLs
                'type': 'scanner'
            }
            for ip, row in scanner_ips.iterrows()
        ]
    
    def _detect_suspicious_ips(self, df: pd.DataFrame) -> List[Dict]:
        """Detect suspicious IPs based on behavior."""
        if 'ip' not in df.columns:
            return []
        
        suspicious = []
        
        # IP frequency analysis
        ip_counts = df['ip'].value_counts()
        avg_requests = ip_counts.mean()
        std_requests = ip_counts.std()
        
        # IPs with unusually high requests
        threshold = avg_requests + (3 * std_requests) if std_requests > 0 else avg_requests * 5
        
        high_freq_ips = ip_counts[ip_counts > threshold]
        
        for ip, count in high_freq_ips.items():
            suspicious.append({
                'ip': ip,
                'request_count': int(count),
                'reason': 'high_frequency',
                'type': 'suspicious'
            })
        
        return suspicious
