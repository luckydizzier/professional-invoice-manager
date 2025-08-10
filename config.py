"""
Configuration management for the Invoice Application
"""

import json
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager for the application"""
    
    DEFAULT_CONFIG = {
        "database": {
            "path": "invoice_qt5.db",
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "max_backups": 10
        },
        "ui": {
            "theme": "default",
            "window_width": 960,
            "window_height": 640,
            "remember_window_size": True,
            "show_tooltips": True,
            "confirm_deletions": True
        },
        "business": {
            "company_name": "",
            "company_address": "",
            "company_tax_id": "",
            "default_vat_rate": 27,
            "currency": "HUF",
            "invoice_number_prefix": "INV"
        },
        "export": {
            "default_format": "pdf",
            "auto_open_after_export": True,
            "export_directory": "exports"
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config_data = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(self.config_data, loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                self.save_config()  # Save default config
        else:
            self.save_config()  # Create default config file
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save config file: {e}")
    
    def get(self, key_path: str, default=None) -> Any:
        """Get configuration value using dot notation (e.g., 'database.path')"""
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config_data
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    
    def _merge_config(self, default: Dict, loaded: Dict) -> None:
        """Recursively merge loaded config with defaults"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    @property
    def db_path(self) -> str:
        """Get database path"""
        return self.get("database.path", "invoice_qt5.db")
    
    @property
    def window_size(self) -> tuple:
        """Get window size"""
        return (self.get("ui.window_width", 960), self.get("ui.window_height", 640))
    
    @property
    def company_info(self) -> Dict[str, str]:
        """Get company information"""
        return {
            "name": self.get("business.company_name", ""),
            "address": self.get("business.company_address", ""),
            "tax_id": self.get("business.company_tax_id", "")
        }


# Global config instance
config = Config()
