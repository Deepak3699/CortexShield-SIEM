"""
Browser Stats Module
====================
Parse User-Agent strings to extract browser, OS, and device info.
"""

import re
import logging
from typing import Dict, List
from collections import Counter
import pandas as pd

logger = logging.getLogger(__name__)


class BrowserStats:
    """
    Parse User-Agent strings to extract browser and OS statistics.
    """
    
    # Browser patterns
    BROWSER_PATTERNS = [
        (r'Chrome/(\d+\.\d+)', 'Chrome'),
        (r'Firefox/(\d+\.\d+)', 'Firefox'),
        (r'Safari/(\d+\.\d+)', 'Safari'),
        (r'Edge/(\d+\.\d+)', 'Edge'),
        (r'OPR/(\d+\.\d+)', 'Opera'),
        (r'MSIE (\d+\.\d+)', 'Internet Explorer'),
        (r'Trident/.*rv:(\d+\.\d+)', 'Internet Explorer'),
        (r'curl/(\d+\.\d+)', 'cURL'),
        (r'Python-urllib/(\d+\.\d+)', 'Python'),
        (r'Go-http-client/(\d+\.\d+)', 'Go'),
        (r'Java/(\d+\.\d+)', 'Java'),
        (r'wget/(\d+\.\d+)', 'Wget'),
    ]
    
    # OS patterns
    OS_PATTERNS = [
        (r'Windows NT 10\.0', 'Windows 10'),
        (r'Windows NT 6\.3', 'Windows 8.1'),
        (r'Windows NT 6\.2', 'Windows 8'),
        (r'Windows NT 6\.1', 'Windows 7'),
        (r'Windows', 'Windows'),
        (r'Mac OS X (\d+_\d+)', 'macOS'),
        (r'Linux', 'Linux'),
        (r'Android (\d+\.\d+)', 'Android'),
        (r'iPhone OS (\d+_\d+)', 'iOS'),
        (r'iPad.*OS (\d+_\d+)', 'iOS'),
    ]
    
    # Bot patterns
    BOT_PATTERNS = [
        r'Googlebot',
        r'Bingbot',
        r'Slurp',  # Yahoo
        r'DuckDuckBot',
        r'Baiduspider',
        r'YandexBot',
        r'facebot',  # Facebook
        r'Twitterbot',
        r'LinkedInBot',
        r'WhatsApp',
        r'TelegramBot',
        r'curl',
        r'wget',
        r'Python',
        r'Go-http-client',
        r'Java',
        r'scrapy',
        r'bot',
        r'crawler',
        r'spider',
    ]
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Analyze User-Agent strings from DataFrame.
        
        Args:
            df: DataFrame with 'user_agent' column
            
        Returns:
            Dict with browser statistics
        """
        if 'user_agent' not in df.columns:
            return {'error': 'No user_agent column found'}
        
        user_agents = df['user_agent'].dropna().tolist()
        
        if not user_agents:
            return {'error': 'No user agent data'}
        
        logger.info(f"Analyzing {len(user_agents)} user agents")
        
        browsers = []
        operating_systems = []
        bots = []
        devices = []
        
        for ua in user_agents:
            ua_str = str(ua)
            
            # Detect browser
            browser = self._detect_browser(ua_str)
            browsers.append(browser)
            
            # Detect OS
            os_name = self._detect_os(ua_str)
            operating_systems.append(os_name)
            
            # Detect bot
            is_bot = self._is_bot(ua_str)
            if is_bot:
                bots.append(browser)
            
            # Detect device type
            device = self._detect_device(ua_str)
            devices.append(device)
        
        # Calculate statistics
        browser_counts = Counter(browsers)
        os_counts = Counter(operating_systems)
        bot_counts = Counter(bots)
        device_counts = Counter(devices)
        
        total = len(user_agents)
        
        result = {
            'total_user_agents': total,
            'browsers': {
                'distribution': dict(browser_counts.most_common(10)),
                'top_browser': browser_counts.most_common(1)[0] if browser_counts else ('Unknown', 0),
                'chrome_percentage': round(browser_counts.get('Chrome', 0) / total * 100, 1),
                'firefox_percentage': round(browser_counts.get('Firefox', 0) / total * 100, 1),
                'safari_percentage': round(browser_counts.get('Safari', 0) / total * 100, 1),
            },
            'operating_systems': {
                'distribution': dict(os_counts.most_common(10)),
                'top_os': os_counts.most_common(1)[0] if os_counts else ('Unknown', 0),
                'windows_percentage': round(sum(v for k, v in os_counts.items() if 'Windows' in k) / total * 100, 1),
                'mac_percentage': round(sum(v for k, v in os_counts.items() if 'macOS' in k or 'Mac' in k) / total * 100, 1),
                'linux_percentage': round(os_counts.get('Linux', 0) / total * 100, 1),
            },
            'bots': {
                'total_bots': len(bots),
                'bot_percentage': round(len(bots) / total * 100, 1),
                'distribution': dict(bot_counts.most_common(10)),
            },
            'devices': {
                'distribution': dict(device_counts.most_common(10)),
                'desktop_percentage': round(device_counts.get('Desktop', 0) / total * 100, 1),
                'mobile_percentage': round(device_counts.get('Mobile', 0) / total * 100, 1),
            }
        }
        
        logger.info(f"Browser stats: {len(browsers)} analyzed, {len(bots)} bots detected")
        
        return result
    
    def _detect_browser(self, ua: str) -> str:
        """Detect browser from User-Agent."""
        # Check for Edge first (contains Chrome)
        if 'Edg/' in ua or 'Edge/' in ua:
            return 'Edge'
        
        for pattern, name in self.BROWSER_PATTERNS:
            if re.search(pattern, ua):
                return name
        
        return 'Other'
    
    def _detect_os(self, ua: str) -> str:
        """Detect operating system from User-Agent."""
        for pattern, name in self.OS_PATTERNS:
            if re.search(pattern, ua):
                return name
        return 'Other'
    
    def _is_bot(self, ua: str) -> bool:
        """Check if User-Agent is a bot."""
        ua_lower = ua.lower()
        for pattern in self.BOT_PATTERNS:
            if pattern.lower() in ua_lower:
                return True
        return False
    
    def _detect_device(self, ua: str) -> str:
        """Detect device type from User-Agent."""
        mobile_patterns = ['Mobile', 'Android', 'iPhone', 'iPad', 'Windows Phone']
        
        for pattern in mobile_patterns:
            if pattern in ua:
                return 'Mobile'
        
        return 'Desktop'
