"""
Example client code for using the POMSicle Agentic Framework API.
This demonstrates how agents can interact with the API.
"""
import requests
import json
from typing import Dict, Any


class PomsicleAgenticClient:
    """Client for interacting with POMSicle Agentic Framework API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API server.
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def create_recipe_from_template(
        self,
        recipe_name: str,
        template_name: str = "Template.xml",
        unit_procedure_name: str = None,
        operation_name: str = None
    ) -> Dict[str, Any]:
        """
        Create a recipe from a template.
        
        Args:
            recipe_name: Name of the recipe.
            template_name: Template file name.
            unit_procedure_name: Unit procedure name (optional).
            operation_name: Operation name (optional).
        
        Returns:
            Response dictionary with success status and details.
        """
        payload = {
            "recipe_name": recipe_name,
            "template_name": template_name
        }
        if unit_procedure_name:
            payload["unit_procedure_name"] = unit_procedure_name
        if operation_name:
            payload["operation_name"] = operation_name
        
        response = self.session.post(
            f"{self.base_url}/api/recipe/create/template",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_custom_recipe(
        self,
        phases: list,
        recipe_name: str = "Assisted",
        template_name: str = "Assisted.xml"
    ) -> Dict[str, Any]:
        """
        Create a custom recipe with specified phases.
        
        Args:
            phases: List of phase names to include.
            recipe_name: Name of the recipe.
            template_name: Template file name.
        
        Returns:
            Response dictionary with success status and details.
        """
        payload = {
            "phases": phases,
            "recipe_name": recipe_name,
            "template_name": template_name
        }
        
        response = self.session.post(
            f"{self.base_url}/api/recipe/create/custom",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def import_recipe(self, filename: str) -> Dict[str, Any]:
        """
        Import a recipe from XML file.
        
        Args:
            filename: Path to XML file.
        
        Returns:
            Response dictionary with success status and details.
        """
        payload = {"filename": filename}
        
        response = self.session.post(
            f"{self.base_url}/api/recipe/import",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def load_inventory(self, filename: str) -> Dict[str, Any]:
        """
        Load inventory from Excel file.
        
        Args:
            filename: Path to Excel file.
        
        Returns:
            Response dictionary with success status and details.
        """
        payload = {"filename": filename}
        
        response = self.session.post(
            f"{self.base_url}/api/inventory/load",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def start_receiving(
        self,
        material: str,
        uom: str,
        containers: int = 1,
        qty_per_container: float = 1.0
    ) -> Dict[str, Any]:
        """
        Start receiving material.
        
        Args:
            material: Material name/ID.
            uom: Unit of measure.
            containers: Number of containers.
            qty_per_container: Quantity per container.
        
        Returns:
            Response dictionary with success status and details.
        """
        payload = {
            "material": material,
            "uom": uom,
            "containers": containers,
            "qty_per_container": qty_per_container
        }
        
        response = self.session.post(
            f"{self.base_url}/api/receiving/start",
            json=payload
        )
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = PomsicleAgenticClient("http://localhost:8000")
    
    # Check health
    print("Health check:", client.health_check())
    
    # Example: Create recipe from template
    try:
        result = client.create_recipe_from_template(
            recipe_name="TestRecipe",
            template_name="Template.xml"
        )
        print("\nRecipe created:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError creating recipe: {e}")
    
    # Example: Create custom recipe
    try:
        result = client.create_custom_recipe(
            phases=["operator_instruction", "record_text", "record_time"],
            recipe_name="CustomTestRecipe"
        )
        print("\nCustom recipe created:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError creating custom recipe: {e}")
    
    # Example: Start receiving
    try:
        result = client.start_receiving(
            material="MATERIAL123",
            uom="kg",
            containers=2,
            qty_per_container=5.0
        )
        print("\nReceiving started:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError starting receiving: {e}")

