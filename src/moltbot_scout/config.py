"""Configuration management for moltbot-repo-scout."""
import os
import yaml
from typing import Dict, Any, List


class Config:
    """Configuration loader and manager."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses default config.yaml
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "config.yaml"
            )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'github': {
                'token': os.getenv('GITHUB_TOKEN', ''),
                'search_queries': [
                    'moltbot trading bot',
                    'moltbot strategy',
                    'trading bot python',
                    'algorithmic trading bot'
                ],
                'max_results_per_query': 20,
            },
            'scoring': {
                'weights': {
                    'stars': 0.3,
                    'age': 0.2,
                    'commits': 0.2,
                    'license': 0.15,
                    'activity': 0.15
                },
                'min_score': 0.3
            },
            'cloner': {
                'clone_dir': 'data/repos',
                'max_depth': 1,
                'timeout': 300
            },
            'security': {
                'scan_secrets': True,
                'scan_patterns': True,
                'secret_patterns': [
                    r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]',
                    r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
                    r'(?i)(token|auth)\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]',
                ],
                'suspicious_patterns': [
                    r'eval\s*\(',
                    r'exec\s*\(',
                    r'__import__\s*\(',
                    r'subprocess\.',
                    r'os\.system\s*\(',
                ]
            },
            'parser': {
                'file_extensions': ['.py'],
                'max_file_size': 1048576,  # 1MB
                'extract_strategies': True,
                'extract_indicators': True,
                'extract_risk_logic': True
            },
            'output': {
                'artifacts_dir': 'artifacts',
                'index_file': 'artifacts/index.json'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key.
        
        Args:
            key: Dot-separated key (e.g., 'github.token')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot-separated key.
        
        Args:
            key: Dot-separated key (e.g., 'github.token')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, path: str = None):
        """Save configuration to file.
        
        Args:
            path: Path to save config. If None, uses original config_path
        """
        save_path = path or self.config_path
        dir_path = os.path.dirname(save_path)
        if dir_path:  # Only create if there's a directory path
            os.makedirs(dir_path, exist_ok=True)
        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
