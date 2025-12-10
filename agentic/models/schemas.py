"""
Pydantic schemas for API request/response models.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


# Recipe Schemas
class RecipeCreateTemplateRequest(BaseModel):
    """Request schema for creating recipe from template."""
    recipe_name: str = Field(..., description="Name of the recipe to create")
    template_name: Optional[str] = Field(default="Template.xml", description="Name of the template XML file")
    unit_procedure_name: Optional[str] = Field(default=None, description="Name of the unit procedure (auto-generated if not provided)")
    operation_name: Optional[str] = Field(default=None, description="Name of the operation (auto-generated if not provided)")


class RecipeCreateCustomRequest(BaseModel):
    """Request schema for creating custom recipe."""
    phases: List[str] = Field(..., description="List of phase/component names to add to the recipe")
    recipe_name: Optional[str] = Field(default="Assisted", description="Name of the recipe")
    template_name: Optional[str] = Field(default="Assisted.xml", description="Name of the template file")
    bom_name: Optional[str] = Field(default=None, description="Name for the BOM to create and attach")
    materials: Optional[List[str]] = Field(default=None, description="List of material IDs to include in the BOM (required if bom_name is provided)")
    bom_path: Optional[str] = Field(default=None, description="Path to an existing BOM XML file to attach (alternative to bom_name)")


class RecipeImportRequest(BaseModel):
    """Request schema for importing recipe."""
    filename: str = Field(..., description="Path to the XML file to import")


# Inventory Schemas
class InventoryLoadRequest(BaseModel):
    """Request schema for loading inventory."""
    filename: str = Field(..., description="Path to the Excel file")


# Receiving Schemas
class ReceivingStartRequest(BaseModel):
    """Request schema for starting receiving."""
    material: str = Field(..., description="Material name/ID to receive")
    uom: str = Field(..., description="Unit of measure")
    containers: Optional[int] = Field(default=1, description="Number of containers")
    qty_per_container: Optional[float] = Field(default=1.0, description="Quantity per container")


# Response Schemas
class BaseResponse(BaseModel):
    """Base response schema."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")


class RecipeResponse(BaseResponse):
    """Response schema for recipe operations."""
    recipe_name: Optional[str] = None
    unit_procedure_name: Optional[str] = None
    operation_name: Optional[str] = None
    template_name: Optional[str] = None
    phases: Optional[List[str]] = None
    filename: Optional[str] = None
    bom_attached: Optional[bool] = None
    bom_path: Optional[str] = None
    bom_name: Optional[str] = None
    materials: Optional[List[str]] = None
    error: Optional[str] = None


class InventoryResponse(BaseResponse):
    """Response schema for inventory operations."""
    filename: Optional[str] = None
    error: Optional[str] = None


class ReceivingResponse(BaseResponse):
    """Response schema for receiving operations."""
    material: Optional[str] = None
    uom: Optional[str] = None
    containers: Optional[int] = None
    qty_per_container: Optional[float] = None
    error: Optional[str] = None

