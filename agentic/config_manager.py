"""
Configuration manager for agentic framework.
"""
import os
import logging
import sys
from pathlib import Path
from typing import Optional, Dict

# Add parent directory to path to import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import config

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for the agentic framework."""
    
    _instance = None
    _settings = None
    _receive_settings = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._settings is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from config files."""
        try:
            self._settings = config(translator='pomsicle')
            logger.info("Configuration loaded successfully")
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load configuration: {e}")
            self._settings = {}
        
        try:
            self._receive_settings = config(translator='pomsicle:receive')
            logger.info("Receiving configuration loaded successfully")
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"Receiving settings not found: {e}")
            self._receive_settings = {}
    
    @property
    def settings(self) -> Dict:
        """Get main settings."""
        return self._settings or {}
    
    @property
    def receive_settings(self) -> Dict:
        """Get receiving settings."""
        return self._receive_settings or {}
    
    def get_username(self) -> Optional[str]:
        """Get username from settings."""
        return self.settings.get('USERNAME')
    
    def get_password(self) -> Optional[str]:
        """Get password from settings."""
        return self.settings.get('PASSWORD')
    
    def reload(self):
        """Reload configuration."""
        logger.info("Reloading configuration...")
        self._settings = None
        self._receive_settings = None
        self._load_config()

