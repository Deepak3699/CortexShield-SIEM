"""
Schema Module
=============
Defines the common schema for normalized log events.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class NormalizedEvent:
    """
    Common schema for ALL log events.
    
    Regardless of original format (Apache, Nginx, IIS, JSON, custom),
    everything gets converted to this structure.
    """
    timestamp: Optional[datetime] = None
    ip: str = "0.0.0.0"
    method: str = "UNKNOWN"
    url: str = "/"
    protocol: str = "HTTP/1.0"
    status: int = 0
    response_size: int = 0
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    
    # Derived fields (calculated, not parsed)
    hour: Optional[int] = None
    day_of_week: Optional[int] = None
    is_error: bool = False
    
    def __post_init__(self):
        """Calculate derived fields."""
        if self.timestamp:
            self.hour = self.timestamp.hour
            self.day_of_week = self.timestamp.weekday()
        
        self.is_error = self.status >= 400
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'ip': self.ip,
            'method': self.method,
            'url': self.url,
            'protocol': self.protocol,
            'status': self.status,
            'response_size': self.response_size,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'hour': self.hour,
            'day_of_week': self.day_of_week,
            'is_error': self.is_error
        }


# Standard field names used across the system
STANDARD_FIELDS = [
    'timestamp',
    'ip',
    'method',
    'url',
    'protocol',
    'status',
    'bytes',
    'user_agent',
    'referer'
]

# Field aliases - different formats use different names
FIELD_ALIASES = {
    'ip': ['ip', 'client_ip', 'remote_addr', 'client_ip_address', 'src_ip', 'source_ip'],
    'timestamp': ['timestamp', 'time', 'datetime', '@timestamp', 'date', 'ts'],
    'method': ['method', 'http_method', 'request_method', 'req_method'],
    'url': ['url', 'path', 'request_uri', 'uri', 'request_url', 'endpoint'],
    'status': ['status', 'status_code', 'response_status', 'http_status', 'code'],
    'bytes': ['bytes', 'body_bytes_sent', 'response_size', 'size', 'length', 'response_bytes'],
    'user_agent': ['user_agent', 'agent', 'http_user_agent', 'ua'],
    'referer': ['referer', 'referrer', 'http_referer', 'http_referrer'],
    'protocol': ['protocol', 'http_protocol', 'http_version']
}
