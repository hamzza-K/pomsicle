"""
BOM Service - Handles Bill of Materials creation and management operations.
"""
import os
import sys
import logging
from typing import Optional, List
from pathlib import Path

# Add parent directory to path to import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bom.bom_template import PomsicleBOMManager
from config import config

logger = logging.getLogger(__name__)


class BOMService:
    """Service for BOM (Bill of Materials) operations."""
    
    def __init__(self, settings: Optional[dict] = None, bom_settings: Optional[dict] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize BOMService.
        
        Args:
            settings: Configuration dictionary. If None, loads from config.
            bom_settings: BOM-specific configuration dictionary. If None, loads from config.
            username: Username for authentication. If None, loads from config.
            password: Password for authentication. If None, loads from config.
        """
        if settings is None:
            try:
                settings = config(translator='pomsicle')
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Configuration error: {e}")
                raise ValueError(f"Failed to load configuration: {e}")
        
        if bom_settings is None:
            try:
                bom_settings = config(translator='pomsicle:bom')
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"BOM settings not found, using defaults: {e}")
                bom_settings = {
                    'LEVEL_ID': '10',
                    'LOCATION_ID': '4',
                    'LOCATION_NAME': 'Herndon'
                }
        
        self.settings = settings
        self.bom_settings = bom_settings
        self.username = username or settings.get('USERNAME')
        self.password = password or settings.get('PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
    
    def create(
        self,
        bom_name: str,
        materials: List[str],
        template_name: str = "Bom_template.xml"
    ) -> dict:
        """
        Create a BOM with specified materials.
        
        Args:
            bom_name: Name of the BOM to create.
            materials: List of material IDs to include in the BOM.
            template_name: Name of the template XML file (default: "Bom_template.xml").
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            if not materials:
                return {
                    "success": False,
                    "message": "At least one material is required to create a BOM.",
                    "bom_name": bom_name
                }
            
            logger.info(f"Creating BOM '{bom_name}' with materials: {materials}")
            
            manager = PomsicleBOMManager(
                self.settings,
                self.bom_settings,
                materials,
                self.username,
                self.password
            )
            
            success = manager.create_template(
                template_name=template_name,
                bom_name=bom_name,
                pull=False
            )
            
            if success:
                logger.info(f"BOM '{bom_name}' created successfully.")
                return {
                    "success": True,
                    "message": f"BOM '{bom_name}' created successfully.",
                    "bom_name": bom_name,
                    "materials": materials,
                    "template_name": template_name
                }
            else:
                logger.error(f"Failed to create BOM '{bom_name}'.")
                return {
                    "success": False,
                    "message": f"Failed to create BOM '{bom_name}'.",
                    "bom_name": bom_name,
                    "materials": materials,
                    "template_name": template_name
                }
        except Exception as e:
            logger.error(f"Error creating BOM: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating BOM: {str(e)}",
                "error": str(e),
                "bom_name": bom_name,
                "materials": materials
            }
    
    def create_and_get_path(
        self,
        bom_name: str,
        materials: List[str],
        template_name: str = "Bom_template.xml"
    ) -> dict:
        """
        Create a BOM and return the path to the generated XML file.
        Useful for attaching BOMs to recipes.
        
        Args:
            bom_name: Name of the BOM to create.
            materials: List of material IDs to include in the BOM.
            template_name: Name of the template XML file (default: "Bom_template.xml").
        
        Returns:
            dict: Result with success status, message, and file path if successful.
        """
        try:
            if not materials:
                return {
                    "success": False,
                    "message": "At least one material is required to create a BOM.",
                    "bom_name": bom_name
                }
            
            logger.info(f"Creating BOM '{bom_name}' with materials: {materials} (returning path)")
            
            manager = PomsicleBOMManager(
                self.settings,
                self.bom_settings,
                materials,
                self.username,
                self.password
            )
            
            bom_file_path = manager.create_template(
                template_name=template_name,
                bom_name=bom_name,
                pull=True
            )
            
            if bom_file_path and os.path.exists(bom_file_path):
                logger.info(f"BOM '{bom_name}' created successfully at: {bom_file_path}")
                return {
                    "success": True,
                    "message": f"BOM '{bom_name}' created successfully.",
                    "bom_name": bom_name,
                    "materials": materials,
                    "template_name": template_name,
                    "file_path": bom_file_path
                }
            else:
                logger.error(f"Failed to create BOM '{bom_name}' or file not found.")
                return {
                    "success": False,
                    "message": f"Failed to create BOM '{bom_name}' or file not found.",
                    "bom_name": bom_name,
                    "materials": materials,
                    "template_name": template_name
                }
        except Exception as e:
            logger.error(f"Error creating BOM: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating BOM: {str(e)}",
                "error": str(e),
                "bom_name": bom_name,
                "materials": materials
            }

