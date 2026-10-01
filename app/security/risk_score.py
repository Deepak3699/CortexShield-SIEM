"""
Risk Score Module
=================
Calculates risk score by combining multiple signals.
NOT just ML - combines rules + ML + behavior.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Calculates risk score by combining multiple signals.
    
    Score = Rule Score + ML Score + Behavior Score
    
    NOT binary (0/1) - gives 0-100 score!
    """
    
    def calculate_risk(self, 
                       rule_threats: Dict, 
                       ml_anomalies: Dict,
                       traffic_stats: Dict) -> Dict:
        """
        Calculate overall risk score.
        
        Args:
            rule_threats: Threats from security rules
            ml_anomalies: Anomalies from ML model
            traffic_stats: Traffic statistics
            
        Returns:
            Dict with risk scores
        """
        # Rule-based score (0-40 points)
        rule_score = self._calculate_rule_score(rule_threats)
        
        # ML anomaly score (0-30 points)
        ml_score = self._calculate_ml_score(ml_anomalies)
        
        # Behavior score (0-30 points)
        behavior_score = self._calculate_behavior_score(rule_threats, traffic_stats)
        
        # Total risk score
        total_score = min(100, rule_score + ml_score + behavior_score)
        
        # Risk level
        risk_level = self._get_risk_level(total_score)
        
        result = {
            'total_risk_score': total_score,
            'risk_level': risk_level,
            'components': {
                'rule_score': rule_score,
                'ml_score': ml_score,
                'behavior_score': behavior_score
            },
            'recommendation': self._get_recommendation(risk_level)
        }
        
        logger.info(f"Risk score: {total_score}/100 ({risk_level})")
        
        return result
    
    def _calculate_rule_score(self, threats: Dict) -> float:
        """Calculate score from security rules (0-40)."""
        score = 0
        
        # SQL injection attempts
        sql_count = len(threats.get('sql_injection', []))
        score += min(15, sql_count * 3)
        
        # XSS attempts
        xss_count = len(threats.get('xss', []))
        score += min(10, xss_count * 2)
        
        # Path traversal
        traversal_count = len(threats.get('path_traversal', []))
        score += min(10, traversal_count * 2)
        
        # Brute force
        brute_force = threats.get('brute_force', [])
        if brute_force:
            score += min(15, len(brute_force) * 5)
        
        # Scanners
        scanners = threats.get('scanners', [])
        if scanners:
            score += min(10, len(scanners) * 2)
        
        return min(40, score)
    
    def _calculate_ml_score(self, anomalies: Dict) -> float:
        """Calculate score from ML anomalies (0-30)."""
        if not anomalies:
            return 0
        
        anomaly_count = anomalies.get('total_anomalies', 0)
        anomaly_rate = anomalies.get('anomaly_percentage', 0)
        
        # Score based on anomaly rate
        if anomaly_rate > 10:
            return 30
        elif anomaly_rate > 5:
            return 20
        elif anomaly_rate > 2:
            return 10
        elif anomaly_rate > 0:
            return 5
        
        return 0
    
    def _calculate_behavior_score(self, threats: Dict, traffic: Dict) -> float:
        """Calculate score from behavior patterns (0-30)."""
        score = 0
        
        # Suspicious IPs
        suspicious_ips = threats.get('suspicious_ips', [])
        score += min(15, len(suspicious_ips) * 3)
        
        # High frequency IPs
        high_freq = [ip for ip in suspicious_ips if ip.get('reason') == 'high_frequency']
        score += min(10, len(high_freq) * 5)
        
        # Error rate
        total_requests = traffic.get('total_requests', 1)
        if total_requests > 0:
            # This is simplified - in production, calculate actual error rate
            score += 5
        
        return min(30, score)
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        if score >= 80:
            return 'CRITICAL'
        elif score >= 60:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level."""
        recommendations = {
            'CRITICAL': 'Immediate action required! Block suspicious IPs and investigate.',
            'HIGH': 'Review security threats and consider blocking malicious IPs.',
            'MEDIUM': 'Monitor closely and review suspicious activity.',
            'LOW': 'Normal activity. Continue monitoring.'
        }
        return recommendations.get(risk_level, 'Unknown risk level')
