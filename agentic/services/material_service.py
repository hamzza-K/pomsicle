"""
Material Service - Handles material creation and management operations.
"""
import os
import sys
import logging
from typing import Optional, Dict
import configparser

# Add parent directory to path to import modules
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from material.material_template import PomsicleMaterialManager
from config import config

logger = logging.getLogger(__name__)


class MaterialService:
    """Service for material operations."""

    def __init__(self, settings: Optional[configparser.SectionProxy | dict] = None, material_settings: Optional[configparser.SectionProxy | dict] = None,
                  location_settings: Optional[configparser.SectionProxy | dict] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize MaterialService.
        
        Args:
            settings: Configuration dictionary. If None, loads from config.
            material_settings: Material specific configuration dictionary. If None, loads from config.
            username: Username for authentication. If None, loads from config.
            password: Password for authentication. If None, loads from config.
        """
        if settings is None:
            try:
                settings = config(translator='pomsicle')
            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Configuration error: {e}")
                raise ValueError(f"Failed to load configuration: {e}")
        
        if material_settings is None:
            try:
                material_settings = config(translator='pomsicle:material')
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Material specific configuration not found: {e}")
                material_settings = {
                    'LEVEL_ID': '10',
                    'LOCATION_ID': '4',
                    'LOCATION_NAME': 'Herndon'
                }


        if location_settings is None:
            try:
                location_settings = config(translator='pomsicle:location')
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Location specific configuration not found: {e}")
                location_settings = {
                    'LEVEL_ID': '10',
                    'LOCATION_ID': '4',
                    'LOCATION_NAME': 'Herndon'
                }
        
        
        self.settings = settings
        self.material_settings = material_settings
        self.location_settings = location_settings
        self.username = username or settings.get('USERNAME')
        self.password = password or settings.get('PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
    
    def create(
        self,
        material_id: str,
        material_description: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        template_name: str = "material_template.xml"
    ) -> dict:
        """
        Create a material and upload it to POMSicle.
        
        Args:
            material_id: ID of the material to create.
            material_description: Description of the material. If None, uses material_id.
            attributes: Dictionary mapping attribId to sValue. e.g., {"Inventory Tracking": "Container", "Inventory UOM": "g"}
            template_name: Name of the template XML file (default: "material_template.xml").
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            logger.info(f"Creating material '{material_id}' with attributes: {attributes}")
            
            manager = PomsicleMaterialManager(
                self.settings,
                self.material_settings,
                self.location_settings,
                self.username,
                self.password
            )
            
            success = manager.create_template(
                material_id=material_id,
                material_description=material_description,
                attributes=attributes or {},
                template_name=template_name,
                pull=False  # We want to upload and import here
            )
            
            if success:
                logger.info(f"Material '{material_id}' created and imported successfully.")
                return {
                    "success": True,
                    "message": f"Material '{material_id}' created and imported successfully.",
                    "material_id": material_id,
                    "material_description": material_description or material_id,
                    "attributes": attributes or {}
                }
            else:
                logger.error(f"Failed to create and import material '{material_id}'.")
                return {
                    "success": False,
                    "message": f"Failed to create and import material '{material_id}'.",
                    "material_id": material_id
                }
        except Exception as e:
            logger.error(f"Error creating material: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating material: {str(e)}",
                "error": str(e)
            }
    
    def create_and_get_path(
        self,
        material_id: str,
        material_description: Optional[str] = None,
        attributes: Optional[Dict[str, str]] = None,
        template_name: str = "material_template.xml"
    ) -> Optional[str]:
        """
        Create a material and return the path to the generated XML file.
        This is useful when the material needs to be used elsewhere.
        
        Args:
            material_id: ID of the material to create.
            material_description: Description of the material. If None, uses material_id.
            attributes: Dictionary mapping attribId to sValue.
            template_name: Name of the template XML file (default: "material_template.xml").
        
        Returns:
            Optional[str]: Path to the generated material XML file, or None if creation failed.
        """
        try:
            logger.info(f"Generating material XML file for '{material_id}' with attributes: {attributes}")
            
            manager = PomsicleMaterialManager(
                self.settings,
                self.material_settings,
                self.location_settings,
                self.username,
                self.password
            )
            
            material_file_path = manager.create_template(
                material_id=material_id,
                material_description=material_description,
                attributes=attributes or {},
                template_name=template_name,
                pull=True  # We want to pull the file path
            )
            
            if material_file_path:
                logger.info(f"Material XML file generated at: {material_file_path}")
                return material_file_path
            else:
                logger.error(f"Failed to generate material XML file for '{material_id}'.")
                return None
        except Exception as e:
            logger.error(f"Error generating material XML file: {e}", exc_info=True)
            return None

