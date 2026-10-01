"""
Database Module
===============
SQLite database for storing analysis results.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles NumPy/Pandas types.
    Pandas analytics produce int64, float64, bool_, ndarray etc.
    which Python's default json.dumps cannot serialize.
    """
    def default(self, obj):
        try:
            import numpy as np
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.bool_):
                return bool(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        # datetime fallback
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "logsentinel.db"


class Database:
    """
    SQLite database for storing analysis results.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analysis results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_size_mb REAL,
                format_detected TEXT,
                format_confidence REAL,
                total_requests INTEGER,
                unique_ips INTEGER,
                total_threats INTEGER,
                sql_injection_count INTEGER,
                xss_count INTEGER,
                brute_force_count INTEGER,
                scanner_count INTEGER,
                ml_anomalies INTEGER,
                anomaly_percentage REAL,
                risk_score INTEGER,
                risk_level TEXT,
                recommendation TEXT,
                full_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Threats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER,
                threat_type TEXT,
                ip TEXT,
                url TEXT,
                timestamp TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id)
            )
        ''')
        
        # Blocked IPs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL UNIQUE,
                reason TEXT,
                risk_score INTEGER,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_by TEXT DEFAULT 'system',
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def save_analysis(self, result: Dict) -> int:
        """Save analysis result to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        file_info = result.get('file_info', {})
        format_info = result.get('format_detected', {})
        traffic = result.get('traffic', {})
        security = result.get('security', {})
        ml = result.get('ml_anomalies', {})
        risk = result.get('risk_score', {})
        
        cursor.execute('''
            INSERT INTO analyses (
                filename, file_size_mb, format_detected, format_confidence,
                total_requests, unique_ips, total_threats,
                sql_injection_count, xss_count, brute_force_count, scanner_count,
                ml_anomalies, anomaly_percentage,
                risk_score, risk_level, recommendation, full_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info.get('file_name', 'unknown'),
            file_info.get('file_size_mb', 0),
            format_info.get('name', 'unknown'),
            format_info.get('confidence', 0),
            traffic.get('total_requests', 0),
            traffic.get('unique_ips', 0),
            security.get('total_threats', 0),
            len(security.get('sql_injection', [])),
            len(security.get('xss', [])),
            len(security.get('brute_force', [])),
            len(security.get('scanners', [])),
            ml.get('total_anomalies', 0),
            ml.get('anomaly_percentage', 0),
            risk.get('total_risk_score', 0),
            risk.get('risk_level', 'LOW'),
            risk.get('recommendation', ''),
            json.dumps(result, cls=NumpyEncoder)
        ))
        
        analysis_id = cursor.lastrowid
        
        # Save threats
        for threat in security.get('sql_injection', []):
            cursor.execute('''
                INSERT INTO threats (analysis_id, threat_type, ip, url, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (analysis_id, 'sql_injection', threat.get('ip'), threat.get('url'), threat.get('timestamp')))
        
        for threat in security.get('xss', []):
            cursor.execute('''
                INSERT INTO threats (analysis_id, threat_type, ip, url, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (analysis_id, 'xss', threat.get('ip'), threat.get('url'), threat.get('timestamp')))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Analysis saved with ID: {analysis_id}")
        return analysis_id
    
    def get_all_analyses(self, limit: int = 50) -> List[Dict]:
        """Get all analysis history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, filename, file_size_mb, format_detected, 
                   total_requests, unique_ips, total_threats,
                   ml_anomalies, risk_score, risk_level, created_at
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """Get full analysis by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM analyses WHERE id = ?', (analysis_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            if result.get('full_result'):
                result['full_result'] = json.loads(result['full_result'])
            return result
        return None
    
    def get_threats_by_analysis(self, analysis_id: int) -> List[Dict]:
        """Get threats for a specific analysis."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM threats WHERE analysis_id = ?', (analysis_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def block_ip(self, ip: str, reason: str, risk_score: int, blocked_by: str = 'admin') -> bool:
        """Block an IP address."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO blocked_ips (ip, reason, risk_score, blocked_by)
                VALUES (?, ?, ?, ?)
            ''', (ip, reason, risk_score, blocked_by))
            conn.commit()
            conn.close()
            logger.info(f"IP blocked: {ip} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Failed to block IP: {e}")
            conn.close()
            return False
    
    def unblock_ip(self, ip: str) -> bool:
        """Unblock an IP address."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE blocked_ips SET is_active = 0 WHERE ip = ?', (ip,))
        conn.commit()
        conn.close()
        
        logger.info(f"IP unblocked: {ip}")
        return True
    
    def get_blocked_ips(self) -> List[Dict]:
        """Get all blocked IPs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blocked_ips WHERE is_active = 1 ORDER BY blocked_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM blocked_ips WHERE ip = ? AND is_active = 1', (ip,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM analyses')
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM threats')
        total_threats = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM blocked_ips WHERE is_active = 1')
        blocked_ips = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(risk_score) FROM analyses')
        avg_risk = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_analyses': total_analyses,
            'total_threats': total_threats,
            'blocked_ips': blocked_ips,
            'avg_risk_score': round(avg_risk, 1)
        }
