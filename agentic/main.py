"""
FastAPI application for POMSicle Agentic Framework.
Provides REST API endpoints for all CLI operations.
"""
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config_manager import ConfigManager
from services.recipe_service import RecipeService
from services.inventory_service import InventoryService
from services.receiving_service import ReceivingService
from services.material_service import MaterialService
from services.bom_service import BOMService
from models.schemas import (
    RecipeCreateTemplateRequest,
    RecipeCreateCustomRequest,
    RecipeImportRequest,
    RecipeResponse,
    InventoryLoadRequest,
    InventoryResponse,
    ReceivingStartRequest,
    ReceivingResponse,
    MaterialCreateRequest,
    MaterialResponse
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

config_manager = ConfigManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    logger.info("Starting POMSicle Agentic Framework API...")
    yield
    logger.info("Shutting down POMSicle Agentic Framework API...")


app = FastAPI(
    title="POMSicle Agentic Framework API",
    description="REST API for POMSicle operations - Converted from CLI to agent-friendly interface",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency functions
def get_recipe_service() -> RecipeService:
    """Dependency to get RecipeService instance."""
    return RecipeService(
        settings=config_manager.settings,
        bom_settings=config_manager.bom_settings,
        username=config_manager.get_username(),
        password=config_manager.get_password()
    )


def get_inventory_service() -> InventoryService:
    """Dependency to get InventoryService instance."""
    return InventoryService(
        settings=config_manager.settings,
        username=config_manager.get_username(),
        password=config_manager.get_password()
    )


def get_receiving_service() -> ReceivingService:
    """Dependency to get ReceivingService instance."""
    return ReceivingService(
        settings=config_manager.settings,
        receive_settings=config_manager.receive_settings,
        username=config_manager.get_username(),
        password=config_manager.get_password()
    )


def get_material_service() -> MaterialService:
    """Dependency to get MaterialService instance."""
    return MaterialService(
        settings=config_manager.settings,
        material_settings=config_manager.material_settings,
        location_settings=config_manager.location_settings,
        username=config_manager.get_username(),
        password=config_manager.get_password()
    )


def get_bom_service() -> BOMService:
    """Dependency to get BOMService instance."""
    return BOMService(
        settings=config_manager.settings,
        location_settings=config_manager.location_settings,
        username=config_manager.get_username(),
        password=config_manager.get_password()
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "POMSicle Agentic Framework API"
    }


# Recipe endpoints
@app.post("/api/recipe/create/template", response_model=RecipeResponse, tags=["Recipe"])
async def create_recipe_from_template(
    request: RecipeCreateTemplateRequest,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Create a recipe from a built-in template.
    
    This endpoint creates a recipe using a predefined template XML file.
    If unit_procedure_name and operation_name are not provided, they will be
    auto-generated from the recipe name.
    """
    try:
        result = service.create_from_template(
            recipe_name=request.recipe_name,
            template_name=request.template_name,
            unit_procedure_name=request.unit_procedure_name,
            operation_name=request.operation_name
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return RecipeResponse(**result)
        
    except ValueError as e:
        logger.error(f"Value error in create_recipe_from_template: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_recipe_from_template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/recipe/create/custom", response_model=RecipeResponse, tags=["Recipe"])
async def create_custom_recipe(
    request: RecipeCreateCustomRequest,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Create a custom recipe with specified phases.
    
    This endpoint creates a custom recipe by combining multiple phases/components.
    The phases are inserted into a base template and then the recipe is created.
    """
    try:
        result = service.create_custom(
            phases=request.phases,
            recipe_name=request.recipe_name,
            template_name=request.template_name,
            bom_name=request.bom_name,
            materials=request.materials,
            bom_path=request.bom_path
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return RecipeResponse(**result)
        
    except ValueError as e:
        logger.error(f"Value error in create_custom_recipe: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_custom_recipe: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/recipe/import", response_model=RecipeResponse, tags=["Recipe"])
async def import_recipe(
    request: RecipeImportRequest,
    service: RecipeService = Depends(get_recipe_service)
):
    """
    Import a recipe from an XML file.
    
    This endpoint imports a recipe from an XML file.
    """
    try:
        result = service.import_recipe(filename=request.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return RecipeResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in import_recipe: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Inventory endpoints
@app.post("/api/inventory/load", response_model=InventoryResponse, tags=["Inventory"])
async def load_inventory(
    request: InventoryLoadRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Load inventory from an Excel file.
    
    This endpoint loads inventory data from an Excel file into the POMS system.
    """
    try:
        result = service.load_from_file(filename=request.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return InventoryResponse(**result)
        
    except ValueError as e:
        logger.error(f"Value error in load_inventory: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in load_inventory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Receiving endpoints
@app.post("/api/receiving/start", response_model=ReceivingResponse, tags=["Receiving"])
async def start_receiving(
    request: ReceivingStartRequest,
    service: ReceivingService = Depends(get_receiving_service)
):
    """
    Start receiving material.
    
    This endpoint initiates the receiving process for a material with specified
    quantity and unit of measure.
    """
    try:
        result = service.start_receiving(
            material=request.material,
            uom=request.uom,
            containers=request.containers,
            qty_per_container=request.qty_per_container
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return ReceivingResponse(**result)
        
    except ValueError as e:
        logger.error(f"Value error in start_receiving: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in start_receiving: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Material endpoints
@app.post("/api/material/create", response_model=MaterialResponse, tags=["Material"])
async def create_material(
    request: MaterialCreateRequest,
    service: MaterialService = Depends(get_material_service)
):
    """
    Create a material.
    
    This endpoint creates a material with specified ID, description, and attributes.
    Attributes are key-value pairs where the key is the attribId and the value is the sValue.
    """

    try:
        result = service.create(
            material_id=request.material_id,
            material_description=request.material_description,
            attributes=request.attributes or config_manager.material_settings,
            template_name=request.template_name or "material_template.xml"
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return MaterialResponse(**result)
        
    except ValueError as e:
        logger.error(f"Value error in create_material: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in create_material: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

