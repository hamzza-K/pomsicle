"""
Receiving Service - Handles material receiving operations.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path to import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from receive.receiving import ReceiveManager
from config import config

logger = logging.getLogger(__name__)


class ReceivingService:
    """Service for receiving operations."""
    
    def __init__(self, settings: Optional[dict] = None, receive_settings: Optional[dict] = None, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize ReceivingService.
        
        Args:
            settings: Configuration dictionary. If None, loads from config.
            receive_settings: Receiving-specific configuration. If None, loads from config.
            username: Username for authentication. If None, loads from config.
            password: Password for authentication. If None, loads from config.
        """
        if settings is None:
            try:
                settings = config(translator='pomsicle')
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Configuration error: {e}")
                raise ValueError(f"Failed to load configuration: {e}")
        
        if receive_settings is None:
            try:
                receive_settings = config(translator='pomsicle:receive')
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Receiving settings not found, using defaults: {e}")
                receive_settings = {}
        
        self.settings = settings
        self.receive_settings = receive_settings
        self.username = username or settings.get('USERNAME')
        self.password = password or settings.get('PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
    
    def start_receiving(
        self,
        material: str,
        uom: str,
        containers: int = 1,
        qty_per_container: float = 1.0
    ) -> dict:
        """
        Start receiving material.
        
        Args:
            material: Material name/ID to receive.
            uom: Unit of measure.
            containers: Number of containers (default: 1).
            qty_per_container: Quantity per container (default: 1.0).
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            if not material or not uom:
                return {
                    "success": False,
                    "message": "Material and UOM are required",
                    "material": material,
                    "uom": uom
                }
            
            logger.info(f"Starting receiving: Material={material}, UOM={uom}, Containers={containers}, Qty={qty_per_container}")
            
            rm = ReceiveManager(self.settings, self.receive_settings, self.username, self.password)
            success = rm.receive(
                material_name=material,
                uom=uom,
                containers=containers,
                qty_per_container=qty_per_container
            )
            
            if success:
                logger.info(f"Material '{material}' received successfully.")
                return {
                    "success": True,
                    "message": f"Material '{material}' received successfully.",
                    "material": material,
                    "uom": uom,
                    "containers": containers,
                    "qty_per_container": qty_per_container
                }
            else:
                logger.error(f"Failed to receive material '{material}'.")
                return {
                    "success": False,
                    "message": f"Failed to receive material '{material}'.",
                    "material": material,
                    "uom": uom
                }
                
        except Exception as e:
            logger.error(f"Error receiving material: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error receiving material: {str(e)}",
                "error": str(e),
                "material": material,
                "uom": uom
            }

