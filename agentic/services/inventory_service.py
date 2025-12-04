"""
Inventory Service - Handles inventory operations.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path to import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from inventory.read_inventory import read_file as read_inventory
from credentials import login
from config import config

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory operations."""
    
    def __init__(self, settings: Optional[dict] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize InventoryService.
        
        Args:
            settings: Configuration dictionary. If None, loads from config.
            username: Username for authentication. If None, loads from config.
            password: Password for authentication. If None, loads from config.
        """
        if settings is None:
            try:
                settings = config(translator='pomsicle')
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Configuration error: {e}")
                raise ValueError(f"Failed to load configuration: {e}")
        
        self.settings = settings
        self.username = username or settings.get('USERNAME')
        self.password = password or settings.get('PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
    
    def load_from_file(self, filename: str) -> dict:
        """
        Load inventory from an Excel file.
        
        Args:
            filename: Path to the Excel file.
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            logger.info(f"Loading inventory from file: {filename}")
            
            # Authenticate
            token_obj = login(username=self.username, password=self.password)
            
            if not token_obj or not hasattr(token_obj, "access_token"):
                return {
                    "success": False,
                    "message": "Authentication failed",
                    "filename": filename
                }
            
            # Load inventory
            read_inventory(token=token_obj.access_token, filename=filename)
            
            logger.info(f"Inventory loaded successfully from {filename}")
            return {
                "success": True,
                "message": f"Inventory loaded successfully from {filename}",
                "filename": filename
            }
            
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            return {
                "success": False,
                "message": f"File not found: {filename}",
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Error loading inventory: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error loading inventory: {str(e)}",
                "error": str(e),
                "filename": filename
            }

