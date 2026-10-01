"""
IP Blocker Module
=================
IP blocking integration with firewall/WAF.
"""

import subprocess
import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class IPBlocker:
    """
    IP blocking with multiple backend support:
    - iptables (Linux firewall)
    - ufw (Ubuntu firewall)
    - Cloudflare WAF (API)
    - Custom webhook
    """
    
    def __init__(self, backend: str = 'local', config: Dict = None):
        self.backend = backend
        self.config = config or {}
        self.blocked_ips_file = Path(__file__).parent.parent.parent / "data" / "blocked_ips.json"
        self._load_blocked_ips()
    
    def _load_blocked_ips(self):
        """Load blocked IPs from file."""
        if self.blocked_ips_file.exists():
            with open(self.blocked_ips_file, 'r') as f:
                self.blocked_ips = json.load(f)
        else:
            self.blocked_ips = {}
    
    def _save_blocked_ips(self):
        """Save blocked IPs to file."""
        with open(self.blocked_ips_file, 'w') as f:
            json.dump(self.blocked_ips, f, indent=2)
    
    def block_ip(self, ip: str, reason: str, risk_score: int) -> Dict:
        """
        Block an IP address.
        
        Args:
            ip: IP address to block
            reason: Reason for blocking
            risk_score: Risk score (0-100)
            
        Returns:
            Dict with block result
        """
        logger.info(f"Blocking IP: {ip} - {reason}")
        
        result = {
            'ip': ip,
            'reason': reason,
            'risk_score': risk_score,
            'backend': self.backend,
            'success': False
        }
        
        try:
            if self.backend == 'iptables':
                result['success'] = self._block_iptables(ip)
            elif self.backend == 'ufw':
                result['success'] = self._block_ufw(ip)
            elif self.backend == 'cloudflare':
                result['success'] = self._block_cloudflare(ip, reason)
            elif self.backend == 'webhook':
                result['success'] = self._block_webhook(ip, reason, risk_score)
            elif self.backend == 'local':
                result['success'] = self._block_local(ip, reason, risk_score)
            else:
                result['success'] = self._block_local(ip, reason, risk_score)
            
            if result['success']:
                self.blocked_ips[ip] = {
                    'reason': reason,
                    'risk_score': risk_score,
                    'backend': self.backend
                }
                self._save_blocked_ips()
                logger.info(f"IP blocked successfully: {ip}")
            
        except Exception as e:
            logger.error(f"Failed to block IP: {e}")
            result['error'] = str(e)
        
        return result
    
    def unblock_ip(self, ip: str) -> Dict:
        """
        Unblock an IP address.
        
        Args:
            ip: IP address to unblock
            
        Returns:
            Dict with unblock result
        """
        logger.info(f"Unblocking IP: {ip}")
        
        result = {
            'ip': ip,
            'success': False
        }
        
        try:
            if self.backend == 'iptables':
                result['success'] = self._unblock_iptables(ip)
            elif self.backend == 'ufw':
                result['success'] = self._unblock_ufw(ip)
            elif self.backend == 'cloudflare':
                result['success'] = self._unblock_cloudflare(ip)
            elif self.backend == 'local':
                result['success'] = True
            else:
                result['success'] = True
            
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
                self._save_blocked_ips()
            
            logger.info(f"IP unblocked: {ip}")
            
        except Exception as e:
            logger.error(f"Failed to unblock IP: {e}")
            result['error'] = str(e)
        
        return result
    
    def get_blocked_ips(self) -> List[Dict]:
        """Get list of blocked IPs."""
        return [
            {'ip': ip, **info}
            for ip, info in self.blocked_ips.items()
        ]
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self.blocked_ips
    
    # ==========================================
    # Backend Implementations
    # ==========================================
    
    def _block_local(self, ip: str, reason: str, risk_score: int) -> bool:
        """Block IP locally (file-based)."""
        return True
    
    def _block_iptables(self, ip: str) -> bool:
        """Block IP using iptables."""
        try:
            subprocess.run(
                ['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"iptables failed: {e}")
            return False
    
    def _unblock_iptables(self, ip: str) -> bool:
        """Unblock IP using iptables."""
        try:
            subprocess.run(
                ['sudo', 'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"iptables unblock failed: {e}")
            return False
    
    def _block_ufw(self, ip: str) -> bool:
        """Block IP using ufw."""
        try:
            subprocess.run(
                ['sudo', 'ufw', 'deny', 'from', ip],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ufw failed: {e}")
            return False
    
    def _unblock_ufw(self, ip: str) -> bool:
        """Unblock IP using ufw."""
        try:
            subprocess.run(
                ['sudo', 'ufw', 'delete', 'deny', 'from', ip],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ufw unblock failed: {e}")
            return False
    
    def _block_cloudflare(self, ip: str, reason: str) -> bool:
        """Block IP using Cloudflare API."""
        import requests
        
        api_token = self.config.get('cloudflare_api_token')
        zone_id = self.config.get('cloudflare_zone_id')
        
        if not api_token or not zone_id:
            logger.error("Cloudflare API token or zone ID not configured")
            return False
        
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/access_rules/rules"
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'mode': 'block',
            'configuration': {
                'target': 'ip',
                'value': ip
            },
            'notes': f'LogSentinel: {reason}'
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    
    def _unblock_cloudflare(self, ip: str) -> bool:
        """Unblock IP using Cloudflare API."""
        import requests
        
        api_token = self.config.get('cloudflare_api_token')
        zone_id = self.config.get('cloudflare_zone_id')
        
        if not api_token or not zone_id:
            return False
        
        # First, find the rule ID
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/firewall/access_rules/rules"
        headers = {'Authorization': f'Bearer {api_token}'}
        params = {'configuration.value': ip}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            rules = response.json().get('result', [])
            if rules:
                rule_id = rules[0]['id']
                delete_url = f"{url}/{rule_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                return delete_response.status_code == 200
        
        return False
    
    def _block_webhook(self, ip: str, reason: str, risk_score: int) -> bool:
        """Block IP using custom webhook."""
        import requests
        
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            logger.error("Webhook URL not configured")
            return False
        
        data = {
            'action': 'block',
            'ip': ip,
            'reason': reason,
            'risk_score': risk_score,
            'source': 'LogSentinel'
        }
        
        response = requests.post(webhook_url, json=data, timeout=10)
        return response.status_code in [200, 201, 202]
