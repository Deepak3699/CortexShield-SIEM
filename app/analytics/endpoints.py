"""
Endpoints Analytics Module
==========================
Analyzes URL endpoints, paths, and query parameters.
"""

import re
import logging
from typing import Dict, List
from collections import Counter
import pandas as pd

logger = logging.getLogger(__name__)


class EndpointAnalyzer:
    """
    Analyzes URL endpoints and paths.
    """
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Analyze URL endpoints from DataFrame.
        
        Args:
            df: DataFrame with 'url' column
            
        Returns:
            Dict with endpoint analytics
        """
        if 'url' not in df.columns:
            return {'error': 'No url column found'}
        
        urls = df['url'].dropna().tolist()
        
        if not urls:
            return {'error': 'No URL data'}
        
        logger.info(f"Analyzing {len(urls)} URLs")
        
        # Extract paths (without query params)
        paths = [self._extract_path(url) for url in urls]
        
        # Extract directories
        directories = [self._extract_directory(url) for url in urls]
        
        # Extract file extensions
        extensions = [self._extract_extension(url) for url in urls]
        
        # Extract query parameters
        has_params = [self._has_params(url) for url in urls]
        
        # URL lengths
        url_lengths = [len(url) for url in urls]
        
        # URL depth
        url_depths = [url.count('/') for url in urls]
        
        # Calculate statistics
        path_counts = Counter(paths)
        dir_counts = Counter(directories)
        ext_counts = Counter(extensions)
        
        # Error URLs
        error_urls = []
        if 'status' in df.columns:
            error_df = df[df['status'] >= 400]
            error_urls = error_df['url'].value_counts().head(10).to_dict()
        
        # Most 404 URLs
        not_found_urls = []
        if 'status' in df.columns:
            not_found_df = df[df['status'] == 404]
            not_found_urls = not_found_df['url'].value_counts().head(10).to_dict()
        
        result = {
            'total_urls': len(urls),
            'unique_urls': len(set(urls)),
            'unique_paths': len(set(paths)),
            'unique_directories': len(set(directories)),
            
            'top_endpoints': dict(path_counts.most_common(20)),
            'top_directories': dict(dir_counts.most_common(10)),
            'file_types': dict(ext_counts.most_common(10)),
            
            'urls_with_params': sum(has_params),
            'params_percentage': round(sum(has_params) / len(urls) * 100, 1),
            
            'avg_url_length': round(sum(url_lengths) / len(url_lengths), 1),
            'max_url_length': max(url_lengths),
            'min_url_length': min(url_lengths),
            
            'avg_url_depth': round(sum(url_depths) / len(url_depths), 1),
            'max_url_depth': max(url_depths),
            
            'error_urls': error_urls,
            'not_found_urls': not_found_urls,
            
            'suspicious_long_urls': [url for url in urls if len(url) > 200][:10],
        }
        
        logger.info(f"Endpoint analysis: {result['unique_urls']} unique URLs, {result['unique_directories']} directories")
        
        return result
    
    def _extract_path(self, url: str) -> str:
        """Extract path without query parameters."""
        return url.split('?')[0].split('#')[0]
    
    def _extract_directory(self, url: str) -> str:
        """Extract top-level directory."""
        path = self._extract_path(url)
        parts = path.strip('/').split('/')
        return f"/{parts[0]}" if parts else "/"
    
    def _extract_extension(self, url: str) -> str:
        """Extract file extension."""
        path = self._extract_path(url)
        if '.' in path.split('/')[-1]:
            return path.split('.')[-1].lower()
        return 'no_extension'
    
    def _has_params(self, url: str) -> bool:
        """Check if URL has query parameters."""
        return '?' in url
