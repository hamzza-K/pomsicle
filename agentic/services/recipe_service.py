"""
Recipe Service - Handles recipe creation and management operations.
"""
import os
import sys
import logging
from typing import Optional, List
from pathlib import Path

# Add parent directory to path to import modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from recipe.builder import RecipeBuilder
from template.recipe_template import PomsicleTemplateManager
from config import config

logger = logging.getLogger(__name__)


class RecipeService:
    """Service for recipe operations."""
    
    def __init__(self, settings: Optional[dict] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize RecipeService.
        
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
    
    def create_from_template(
        self,
        recipe_name: str,
        template_name: str = "Template.xml",
        unit_procedure_name: Optional[str] = None,
        operation_name: Optional[str] = None
    ) -> dict:
        """
        Create a recipe from a built-in template.
        
        Args:
            recipe_name: Name of the recipe to create.
            template_name: Name of the template XML file (default: "Template.xml").
            unit_procedure_name: Name of the unit procedure (auto-generated if None).
            operation_name: Name of the operation (auto-generated if None).
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            # Auto-generate UP and OP names if only recipe name provided
            if recipe_name and not unit_procedure_name and not operation_name:
                logger.info(f"Auto-generating UP/OP names from recipe '{recipe_name}'.")
                unit_procedure_name = f"{recipe_name}_UP"
                operation_name = f"{recipe_name}_OP"
            
            logger.info(f"Creating recipe from template: {template_name}")
            logger.debug(f"Recipe: {recipe_name}, UP: {unit_procedure_name}, OP: {operation_name}")
            
            manager = PomsicleTemplateManager(self.settings, self.username, self.password)
            success = manager.create_template(
                template_name=template_name,
                recipe_name=recipe_name,
                unit_procedure_name=unit_procedure_name,
                operation_name=operation_name
            )
            
            if success:
                logger.info(f"Recipe '{recipe_name}' created successfully from template '{template_name}'.")
                return {
                    "success": True,
                    "message": f"Recipe '{recipe_name}' created successfully.",
                    "recipe_name": recipe_name,
                    "unit_procedure_name": unit_procedure_name,
                    "operation_name": operation_name,
                    "template_name": template_name
                }
            else:
                logger.error(f"Failed to create recipe '{recipe_name}' from template '{template_name}'.")
                return {
                    "success": False,
                    "message": f"Failed to create recipe '{recipe_name}'.",
                    "recipe_name": recipe_name,
                    "template_name": template_name
                }
        except Exception as e:
            logger.error(f"Error creating recipe from template: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating recipe: {str(e)}",
                "error": str(e)
            }
    
    def create_custom(
        self,
        phases: List[str],
        recipe_name: str = "Assisted",
        template_name: str = "Assisted.xml",
        bom_path: Optional[str] = None
    ) -> dict:
        """
        Create a custom recipe with specified phases.
        
        Args:
            phases: List of phase/component names to add to the recipe.
            recipe_name: Name of the recipe (default: "Assisted").
            template_name: Name of the template file (default: "Assisted.xml").
            bom_path: Optional path to a BOM XML file to attach to the recipe.
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            logger.info(f"Creating custom recipe '{recipe_name}' with phases: {phases}")
            
            builder = RecipeBuilder()
            current_dir = os.path.dirname(os.path.abspath(__file__))
    
            project_root = Path(current_dir).parent.parent
            template_folder = project_root / "template"
            output_file = template_folder / template_name
            
            # Insert components
            builder.insert_components(phases, str(output_file))
            logger.info(f"Custom recipe template created with phases: {' → '.join(phases)}")
            
            # Attach BOM if provided
            if bom_path:
                if not os.path.exists(bom_path):
                    logger.warning(f"BOM file not found: {bom_path}. Skipping attachment.")
                else:
                    builder.attach_bill(bom_path=bom_path, output_path=str(output_file))
                    logger.info(f"Attached BOM to recipe template: {bom_path}")
            
            # Now create the recipe from the generated template
            result = self.create_from_template(
                recipe_name=recipe_name,
                template_name=template_name,
                unit_procedure_name=None,
                operation_name=None
            )
            
            if result["success"]:
                result["phases"] = phases
                result["message"] = f"Custom recipe '{recipe_name}' created successfully with phases: {', '.join(phases)}"
                if bom_path:
                    result["bom_attached"] = True
                    result["bom_path"] = bom_path
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating custom recipe: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating custom recipe: {str(e)}",
                "error": str(e)
            }
    
    def import_recipe(self, filename: str) -> dict:
        """
        Import a recipe from an XML file.
        
        Args:
            filename: Path to the XML file to import.
        
        Returns:
            dict: Result with success status and message.
        """
        try:
            logger.info(f"Importing recipe from: {filename}")
            
            # Check if file exists
            if not os.path.exists(filename):
                return {
                    "success": False,
                    "message": f"File not found: {filename}",
                    "filename": filename
                }
            
            # TODO: Implement import logic
            return {
                "success": True,
                "message": f"Recipe imported from {filename}",
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Error importing recipe: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Error importing recipe: {str(e)}",
                "error": str(e),
                "filename": filename
            }

