"""
Traffic Analytics Module
========================
Analyzes traffic patterns from normalized log data.
"""

import logging
from typing import Dict
import pandas as pd

logger = logging.getLogger(__name__)


class TrafficAnalyzer:
    """
    Analyzes traffic patterns.
    
    This is NORMAL PYTHON - no ML needed!
    """
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Analyze traffic patterns.
        
        Args:
            df: Normalized DataFrame
            
        Returns:
            Dict with traffic analytics
        """
        logger.info(f"Analyzing traffic for {len(df)} events")
        
        result = {
            'total_requests': len(df),
            'unique_ips': df['ip'].nunique() if 'ip' in df.columns else 0,
            'requests_per_hour': self._hourly_distribution(df),
            'requests_per_day': self._daily_distribution(df),
            'peak_hours': self._peak_hours(df),
            'traffic_trend': self._traffic_trend(df)
        }
        
        return result
    
    def _hourly_distribution(self, df: pd.DataFrame) -> Dict:
        """Get request distribution by hour."""
        if 'hour' not in df.columns:
            return {}
        
        return df['hour'].value_counts().sort_index().to_dict()
    
    def _daily_distribution(self, df: pd.DataFrame) -> Dict:
        """Get request distribution by day of week."""
        if 'day_of_week' not in df.columns:
            return {}
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        counts = df['day_of_week'].value_counts().sort_index()
        
        return {days[i]: counts.get(i, 0) for i in range(7)}
    
    def _peak_hours(self, df: pd.DataFrame, top_n: int = 3) -> Dict:
        """Get peak traffic hours."""
        if 'hour' not in df.columns:
            return {}
        
        hourly = df['hour'].value_counts().nlargest(top_n)
        return {f"{hour}:00": count for hour, count in hourly.items()}
    
    def _traffic_trend(self, df: pd.DataFrame) -> Dict:
        """Get traffic trend over time."""
        if 'timestamp' not in df.columns:
            return {}
        
        try:
            # Group by date
            df['date'] = df['timestamp'].dt.date
            daily = df.groupby('date').size()
            
            return {
                'dates': [str(d) for d in daily.index.tolist()],
                'counts': daily.values.tolist()
            }
        except Exception:
            return {}
