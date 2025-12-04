# Knowledge Base Azure Function

This Azure Function provides an API endpoint to retrieve information from Azure Cognitive Search Knowledge Base.

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```
   
   Or update `local.settings.json` with your Azure Search credentials.

3. **Run locally:**
   ```bash
   func start
   ```

### Azure Deployment

1. **Set Application Settings in Azure Portal:**
   - `AZURE_SEARCH_ENDPOINT`: Your Azure Search endpoint
   - `AZURE_SEARCH_API_KEY`: Your Azure Search API key
   - `KB_NAME`: Knowledge base name (default: "knowledgebase-phases")
   - `KB_SOURCE_NAME`: Knowledge source name (default: "knowledgesource-phases")

2. **Deploy using Azure Functions Core Tools:**
   ```bash
   func azure functionapp publish <your-function-app-name>
   ```

## API Usage

### Endpoint
`POST /api/knowledgebase`

### Request Body
```json
{
  "assistant_message": "The name of the phases are usually the file names, only return those names. Finally append a list of phases to be added.",
  "user_message": "Give me your analysis and best suited phases to create the recipe with the following requirements: ...",
  "include_references": true,
  "include_reference_source_data": true,
  "always_query_source": false,
  "include_activity": true
}
```

### Response
```json
{
  "success": true,
  "response": "Response text from knowledge base..."
}
```

### Example using curl
```bash
curl -X POST http://localhost:7071/api/knowledgebase \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_message": "The name of the phases are usually the file names, only return those names.",
    "user_message": "Give me phases for testing vials"
  }'
```

## Code Structure

- `knowledgebase_service.py`: Service class for knowledge base operations
- `function_app.py`: Azure Function entry point
- `local.settings.json`: Local development settings (not committed to git)
- `host.json`: Azure Functions host configuration
- `.env`: Environment variables (not committed to git)

## Logging

The function uses Python's logging module with INFO level by default. Logs are automatically sent to Application Insights when deployed to Azure.

## Security

⚠️ **Important**: Never commit `.env` or `local.settings.json` files containing API keys to version control. Use Azure Key Vault or Application Settings for production deployments.

