# POMSicle Agentic Framework

This is the agentic framework version of POMSicle CLI, providing REST API endpoints for all CLI operations. This allows AI agents and other systems to interact with POMSicle programmatically.

## Overview

The agentic framework exposes all CLI functionality through FastAPI endpoints, making it easy for agents to:
- Create recipes from templates
- Create custom recipes with specific phases
- Import recipes from XML files
- Load inventory from Excel files
- Start material receiving operations

## Installation

1. **Install dependencies:**
   ```bash
   cd agentic
   pip install -r requirements.txt
   ```

2. **Configure your settings:**
   - Ensure your `config/config.cfg` file is properly configured
   - The framework will automatically load settings from your existing configuration

## Running the API

### Development Mode

```bash
cd agentic
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## API Endpoints

### Health Check

**GET** `/health`
- Returns API health status

### Recipe Operations

#### Create Recipe from Template

**POST** `/api/recipe/create/template`

Request body:
```json
{
  "recipe_name": "MyRecipe",
  "template_name": "Template.xml",
  "unit_procedure_name": "MyRecipe_UP",  // Optional, auto-generated if not provided
  "operation_name": "MyRecipe_OP"      // Optional, auto-generated if not provided
}
```

Response:
```json
{
  "success": true,
  "message": "Recipe 'MyRecipe' created successfully.",
  "recipe_name": "MyRecipe",
  "unit_procedure_name": "MyRecipe_UP",
  "operation_name": "MyRecipe_OP",
  "template_name": "Template.xml"
}
```

#### Create Custom Recipe

**POST** `/api/recipe/create/custom`

Request body:
```json
{
  "phases": ["operator_instruction", "record_text", "record_time"],
  "recipe_name": "CustomRecipe",
  "template_name": "Assisted.xml"
}
```

Response:
```json
{
  "success": true,
  "message": "Custom recipe 'CustomRecipe' created successfully with phases: operator_instruction, record_text, record_time",
  "recipe_name": "CustomRecipe",
  "phases": ["operator_instruction", "record_text", "record_time"]
}
```

#### Import Recipe

**POST** `/api/recipe/import`

Request body:
```json
{
  "filename": "/path/to/recipe.xml"
}
```

### Inventory Operations

#### Load Inventory

**POST** `/api/inventory/load`

Request body:
```json
{
  "filename": "/path/to/inventory.xlsx"
}
```

### Receiving Operations

#### Start Receiving

**POST** `/api/receiving/start`

Request body:
```json
{
  "material": "MATERIAL123",
  "uom": "kg",
  "containers": 5,
  "qty_per_container": 10.5
}
```

## Example Usage

### Using curl

```bash
# Create recipe from template
curl -X POST "http://localhost:8000/api/recipe/create/template" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_name": "TestRecipe"
  }'

# Create custom recipe
curl -X POST "http://localhost:8000/api/recipe/create/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "phases": ["operator_instruction", "record_text"],
    "recipe_name": "CustomTest"
  }'

# Start receiving
curl -X POST "http://localhost:8000/api/receiving/start" \
  -H "Content-Type: application/json" \
  -d '{
    "material": "MATERIAL123",
    "uom": "kg",
    "containers": 2,
    "qty_per_container": 5.0
  }'
```

### Using Python

```python
import requests

# Create recipe from template
response = requests.post(
    "http://localhost:8000/api/recipe/create/template",
    json={
        "recipe_name": "MyRecipe",
        "template_name": "Template.xml"
    }
)
print(response.json())

# Create custom recipe
response = requests.post(
    "http://localhost:8000/api/recipe/create/custom",
    json={
        "phases": ["operator_instruction", "record_text"],
        "recipe_name": "CustomRecipe"
    }
)
print(response.json())
```

## Architecture

The framework is organized as follows:

```
agentic/
├── main.py                 # FastAPI application entry point
├── config_manager.py       # Configuration management
├── models/
│   └── schemas.py         # Pydantic request/response models
├── services/
│   ├── recipe_service.py  # Recipe operations service
│   ├── inventory_service.py  # Inventory operations service
│   └── receiving_service.py   # Receiving operations service
└── requirements.txt       # Python dependencies
```

### Service Layer

Each service class wraps the corresponding CLI functionality:
- `RecipeService`: Handles all recipe-related operations
- `InventoryService`: Handles inventory loading
- `ReceivingService`: Handles material receiving

### Configuration

The framework uses the same configuration system as the CLI, loading settings from `config/config.cfg`. The `ConfigManager` class provides a singleton pattern for accessing configuration throughout the application.

## Error Handling

All endpoints return structured error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message"
}
```

HTTP status codes:
- `200`: Success
- `400`: Bad request (validation errors, missing parameters)
- `500`: Internal server error

## Logging

The framework uses Python's logging module. Logs are output to the console with timestamps and log levels. Configure logging levels as needed in `main.py`.

## Security Considerations

For production deployment:
1. Add authentication/authorization (API keys, OAuth, etc.)
2. Configure CORS appropriately (currently allows all origins)
3. Use HTTPS
4. Add rate limiting
5. Validate and sanitize all inputs
6. Use environment variables for sensitive configuration

## Development

To extend the framework:
1. Add new service methods in the appropriate service class
2. Create Pydantic schemas in `models/schemas.py`
3. Add FastAPI endpoints in `main.py`
4. Update this README with new endpoint documentation

## License

Same as the main POMSicle project.

