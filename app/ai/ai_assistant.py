"""
AI Assistant Module
===================
Uses LLM to understand unknown log formats.
Supports: OpenAI, Claude, Gemini, Local LLM (Ollama)
"""

import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AIAssistant:
    """
    AI assistant for unknown log formats.
    
    Supports multiple AI providers:
    - OpenAI (GPT-4)
    - Claude (Anthropic)
    - Gemini (Google)
    - Ollama (Local, FREE)
    - Smart Guess (Fallback, no API needed)
    """
    
    def __init__(self, provider: str = None, api_key: str = None):
        self.provider = provider or os.getenv('AI_PROVIDER', 'smart_guess')
        self.api_key = api_key or os.getenv('AI_API_KEY')
        self.max_sample_lines = 200
        
        # Initialize client based on provider
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize AI client based on provider."""
        
        if self.provider == 'openai' and self.api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("openai package not installed")
        
        elif self.provider == 'claude' and self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("Claude client initialized")
            except ImportError:
                logger.warning("anthropic package not installed")
        
        elif self.provider == 'gemini' and self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized")
            except ImportError:
                logger.warning("google-generativeai package not installed")
        
        elif self.provider == 'ollama':
            try:
                import requests
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    self.client = 'ollama'
                    logger.info("Ollama client initialized")
            except Exception:
                logger.warning("Ollama not running on localhost:11434")
        
        if not self.client:
            logger.info("Using Smart Guess (no AI API)")
    
    def suggest_parser_config(self, sample_lines: List[str], analysis: Dict) -> Dict:
        """
        Suggest parser configuration for unknown format.
        
        Args:
            sample_lines: Sample lines from the log file
            analysis: Analysis of the unknown format
            
        Returns:
            Suggested parser configuration
        """
        # Try AI if available
        if self.client and self.client != 'ollama':
            try:
                return self._call_ai(sample_lines, analysis)
            except Exception as e:
                logger.error(f"AI call failed: {e}")
                return self._smart_guess(sample_lines, analysis)
        
        elif self.client == 'ollama':
            try:
                return self._call_ollama(sample_lines, analysis)
            except Exception as e:
                logger.error(f"Ollama call failed: {e}")
                return self._smart_guess(sample_lines, analysis)
        
        else:
            return self._smart_guess(sample_lines, analysis)
    
    def _call_ai(self, sample_lines: List[str], analysis: Dict) -> Dict:
        """Call AI API (OpenAI/Claude/Gemini)."""
        prompt = self._build_prompt(sample_lines, analysis)
        
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        
        elif self.provider == 'claude':
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(message.content[0].text)
        
        elif self.provider == 'gemini':
            response = self.client.generate_content(prompt)
            return json.loads(response.text)
        
        return self._smart_guess(sample_lines, analysis)
    
    def _call_ollama(self, sample_lines: List[str], analysis: Dict) -> Dict:
        """Call local Ollama LLM (FREE)."""
        import requests
        
        prompt = self._build_prompt(sample_lines, analysis)
        
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'llama2',
            'prompt': prompt,
            'stream': False
        })
        
        result = response.json()
        return json.loads(result['response'])
    
    def _build_prompt(self, sample_lines: List[str], analysis: Dict) -> str:
        """Build prompt for AI."""
        prompt = """You are a log format analyzer. Given sample log lines, suggest a parser configuration.

SAMPLE LINES:
"""
        for i, line in enumerate(sample_lines[:10]):
            prompt += f"{i+1}. {line}\n"
        
        prompt += f"""
ANALYSIS:
- Has IP addresses: {analysis.get('has_ip', False)}
- Has timestamps: {analysis.get('has_timestamp', False)}
- Has HTTP methods: {analysis.get('has_method', False)}
- Has status codes: {analysis.get('has_status', False)}
- Has URLs: {analysis.get('has_url', False)}
- Possible delimiter: {analysis.get('possible_delimiter', 'none')}

Return JSON with:
{{
    "format": "custom_delimited",
    "delimiter": "|",
    "fields": ["timestamp", "ip", "method", "url", "status"],
    "timestamp_format": "%d-%m-%Y %H:%M:%S",
    "confidence": 0.85
}}
"""
        return prompt
    
    def _smart_guess(self, sample_lines: List[str], analysis: Dict) -> Dict:
        """
        Smart guess based on analysis.
        No AI API needed - pure Python logic.
        """
        # Guard: analysis can be None if called with a known-format that failed validation
        if analysis is None:
            analysis = {}
        delimiter = analysis.get('possible_delimiter')
        
        if delimiter:
            first_line = sample_lines[0] if sample_lines else ''
            fields = first_line.split(delimiter)
            num_fields = len(fields)
            
            field_names = self._guess_field_names(num_fields, analysis)
            
            return {
                'format': 'custom_delimited',
                'type': 'delimited',
                'delimiter': delimiter,
                'fields': field_names,
                'timestamp_format': self._guess_timestamp_format(sample_lines),
                'confidence': 0.6
            }
        
        # Space-delimited
        first_line = sample_lines[0] if sample_lines else ''
        fields = first_line.split()
        num_fields = len(fields)
        
        field_names = self._guess_field_names(num_fields, analysis)
        
        return {
            'format': 'custom_space_delimited',
            'type': 'delimited',
            'delimiter': ' ',
            'fields': field_names,
            'timestamp_format': self._guess_timestamp_format(sample_lines),
            'confidence': 0.5
        }
    
    def _guess_field_names(self, num_fields: int, analysis: Dict) -> List[str]:
        """Guess field names based on analysis."""
        fields = []
        
        if analysis.get('has_timestamp'):
            fields.append('timestamp')
        if analysis.get('has_ip'):
            fields.append('ip')
        if analysis.get('has_method'):
            fields.append('method')
        if analysis.get('has_url'):
            fields.append('url')
        if analysis.get('has_status'):
            fields.append('status')
        
        while len(fields) < num_fields:
            fields.append(f'field_{len(fields) + 1}')
        
        return fields[:num_fields]
    
    def _guess_timestamp_format(self, sample_lines: List[str]) -> str:
        """Guess timestamp format."""
        import re
        
        for line in sample_lines[:10]:
            if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line):
                return '%Y-%m-%dT%H:%M:%S'
            if re.search(r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}', line):
                return '%d/%b/%Y:%H:%M:%S %z'
            if re.search(r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', line):
                return '%d-%m-%Y %H:%M:%S'
            if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
                return '%Y-%m-%d %H:%M:%S'
        
        return None
    
    def get_provider_info(self) -> Dict:
        """Get current AI provider info."""
        return {
            'provider': self.provider,
            'has_api_key': bool(self.api_key),
            'client_initialized': bool(self.client),
            'mode': 'AI' if self.client else 'Smart Guess'
        }
