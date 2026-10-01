"""
Feature Engineering Module
==========================
Creates features for ML model from normalized log data.
"""

import logging
from typing import Dict, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Creates features for ML anomaly detection.
    
    Features are PER IP PER TIME WINDOW, not per individual request.
    This gives the model behavioral context.
    """
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features for ML model using fast vectorized operations.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            DataFrame with one row per IP and behavioral features
        """
        logger.info(f"Creating features from {len(df)} events")
        
        if df.empty:
            return pd.DataFrame()

        # Prepare helper DataFrame for fast vectorization
        temp_df = pd.DataFrame({'ip': df['ip']})
        
        temp_df['url'] = df['url'] if 'url' in df.columns else ''
        temp_df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(200) if 'status' in df.columns else 200
        temp_df['method'] = df['method'] if 'method' in df.columns else 'GET'
        temp_df['hour'] = pd.to_numeric(df['hour'], errors='coerce').fillna(0) if 'hour' in df.columns else 0
        temp_df['bytes'] = pd.to_numeric(df['bytes'], errors='coerce').fillna(0) if 'bytes' in df.columns else 0

        # Vectorized feature calculations
        temp_df['url_len'] = temp_df['url'].astype(str).str.len()
        temp_df['has_params'] = temp_df['url'].astype(str).str.contains(r'\?', regex=True).astype(int)
        
        status = temp_df['status']
        temp_df['success'] = (status < 400).astype(int)
        temp_df['error'] = (status >= 400).astype(int)
        temp_df['status_2xx'] = ((status >= 200) & (status < 300)).astype(int)
        temp_df['status_3xx'] = ((status >= 300) & (status < 400)).astype(int)
        temp_df['status_4xx'] = ((status >= 400) & (status < 500)).astype(int)
        temp_df['status_5xx'] = (status >= 500).astype(int)
        
        method = temp_df['method'].astype(str).str.upper()
        temp_df['method_get'] = (method == 'GET').astype(int)
        temp_df['method_post'] = (method == 'POST').astype(int)
        temp_df['method_put'] = (method == 'PUT').astype(int)
        temp_df['method_delete'] = (method == 'DELETE').astype(int)
        
        hour = temp_df['hour']
        temp_df['night'] = ((hour >= 0) & (hour < 6)).astype(int)
        
        bytes_col = temp_df['bytes']

        # Groupby aggregation (single pass C-accelerated in Pandas)
        feature_df = temp_df.groupby('ip').agg(
            total_requests=('url', 'count'),
            unique_urls=('url', 'nunique'),
            success_count=('success', 'sum'),
            error_count=('error', 'sum'),
            status_2xx=('status_2xx', 'sum'),
            status_3xx=('status_3xx', 'sum'),
            status_4xx=('status_4xx', 'sum'),
            status_5xx=('status_5xx', 'sum'),
            method_get=('method_get', 'sum'),
            method_post=('method_post', 'sum'),
            method_put=('method_put', 'sum'),
            method_delete=('method_delete', 'sum'),
            avg_url_length=('url_len', 'mean'),
            max_url_length=('url_len', 'max'),
            urls_with_params=('has_params', 'sum'),
            unique_hours=('hour', 'nunique'),
            night_requests=('night', 'sum'),
            total_bytes=('bytes', 'sum'),
            avg_bytes=('bytes', 'mean'),
            max_bytes=('bytes', 'max')
        ).reset_index()

        feature_df['error_rate'] = feature_df['error_count'] / feature_df['total_requests'].clip(lower=1)

        logger.info(f"Created {len(feature_df)} feature rows with {len(feature_df.columns)} features")
        
        return feature_df
    
    def get_feature_columns(self, feature_df: pd.DataFrame) -> List[str]:
        """Get list of feature columns for ML model."""
        exclude = ['ip']
        return [col for col in feature_df.columns if col not in exclude]
