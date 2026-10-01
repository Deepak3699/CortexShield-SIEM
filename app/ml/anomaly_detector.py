"""
Anomaly Detector Module
=======================
Isolation Forest based anomaly detection.
"""

import logging
from typing import Dict, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Isolation Forest anomaly detector.
    
    Trains on EACH file (not pre-trained) for accuracy.
    """
    
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model = None
        self.scaler = None
        self.feature_cols = None
        self.model_info = {}
    
    def train_and_predict(self, feature_df: pd.DataFrame, feature_cols: list) -> Tuple[pd.DataFrame, Dict]:
        """
        Train model and make predictions on same data.
        
        Args:
            feature_df: DataFrame with features
            feature_cols: List of feature column names
            
        Returns:
            Tuple of (predictions_df, model_info)
        """
        logger.info(f"Training Isolation Forest on {len(feature_df)} samples")
        
        self.feature_cols = feature_cols
        
        # Prepare data
        X = feature_df[feature_cols].fillna(0)
        
        # Adjust contamination for small datasets
        contamination = self.contamination
        if len(feature_df) < 50:
            contamination = 0.1
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        
        # Make predictions
        raw_predictions = self.model.predict(X_scaled)
        
        # Convert: -1 → 1 (anomaly), 1 → 0 (normal)
        feature_df['is_anomaly'] = (raw_predictions == -1).astype(int)
        
        # Get anomaly scores
        raw_scores = self.model.score_samples(X_scaled)
        
        # Normalize scores to 0-1 range
        min_score = raw_scores.min()
        max_score = raw_scores.max()
        
        if max_score != min_score:
            feature_df['anomaly_score'] = 1 - ((raw_scores - min_score) / (max_score - min_score))
        else:
            feature_df['anomaly_score'] = 0.0
        
        # Model info
        self.model_info = {
            'type': 'Isolation Forest',
            'trained_on': int(len(feature_df)),
            'contamination': f"{contamination * 100:.1f}%",
            'features': len(feature_cols),
            'anomalies_detected': int(feature_df['is_anomaly'].sum())
        }
        
        logger.info(f"Detected {self.model_info['anomalies_detected']} anomalies")
        
        return feature_df, self.model_info
