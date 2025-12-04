# Azure Functions Deployment Guide

## Prerequisites

1. **Azure Functions Core Tools** installed:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Azure CLI** installed and logged in:
   ```bash
   az login
   ```

3. **Python 3.9+** installed

## Local Development Setup

1. **Install dependencies:**
   ```bash
   cd agentic
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Create a `.env` file (copy from `.env.example` if available) or update `local.settings.json`:
   ```json
   {
     "Values": {
       "AZURE_SEARCH_ENDPOINT": "https://your-endpoint.search.windows.net",
       "AZURE_SEARCH_API_KEY": "your-api-key",
       "KB_NAME": "knowledgebase-phases",
       "KB_SOURCE_NAME": "knowledgesource-phases"
     }
   }
   ```

3. **Run locally:**
   ```bash
   func start
   ```

   The function will be available at: `http://localhost:7071/api/knowledgebase`

## Deploy to Azure

### Option 1: Using Azure Functions Core Tools

1. **Create a Function App** (if not already created):
   ```bash
   az functionapp create \
     --resource-group <your-resource-group> \
     --consumption-plan-location <location> \
     --runtime python \
     --runtime-version 3.9 \
     --functions-version 4 \
     --name <your-function-app-name> \
     --storage-account <your-storage-account>
   ```

2. **Set Application Settings:**
   ```bash
   az functionapp config appsettings set \
     --name <your-function-app-name> \
     --resource-group <your-resource-group> \
     --settings \
       AZURE_SEARCH_ENDPOINT="https://your-endpoint.search.windows.net" \
       AZURE_SEARCH_API_KEY="your-api-key" \
       KB_NAME="knowledgebase-phases" \
       KB_SOURCE_NAME="knowledgesource-phases"
   ```

3. **Deploy the function:**
   ```bash
   func azure functionapp publish <your-function-app-name>
   ```

### Option 2: Using Azure Portal

1. **Create Function App** in Azure Portal:
   - Runtime stack: Python
   - Version: 3.9 or higher
   - Plan: Consumption (Serverless)

2. **Configure Application Settings:**
   - Go to Configuration → Application settings
   - Add the following settings:
     - `AZURE_SEARCH_ENDPOINT`
     - `AZURE_SEARCH_API_KEY`
     - `KB_NAME`
     - `KB_SOURCE_NAME`

3. **Deploy code:**
   - Use VS Code Azure Functions extension, or
   - Use Azure CLI, or
   - Use GitHub Actions/CI/CD pipeline

## Testing the Deployed Function

### Using curl:
```bash
curl -X POST https://<your-function-app-name>.azurewebsites.net/api/knowledgebase \
  -H "Content-Type: application/json" \
  -H "x-functions-key: <your-function-key>" \
  -d '{
    "assistant_message": "The name of the phases are usually the file names.",
    "user_message": "Give me phases for testing vials"
  }'
```

### Using Python:
```python
import requests
import json

url = "https://<your-function-app-name>.azurewebsites.net/api/knowledgebase"
headers = {
    "Content-Type": "application/json",
    "x-functions-key": "<your-function-key>"
}
data = {
    "assistant_message": "The name of the phases are usually the file names.",
    "user_message": "Give me phases for testing vials"
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

## Function Keys

To get your function key:
1. Go to Azure Portal → Your Function App → Functions → KnowledgeBaseRetrieval → Function Keys
2. Copy the default key or create a new one

## Monitoring

- **Application Insights**: Automatically enabled for logging and monitoring
- **Logs**: View in Azure Portal under "Log stream" or "Application Insights"
- **Metrics**: Monitor function execution, errors, and performance in Application Insights

## Troubleshooting

1. **Import errors**: Ensure all dependencies are in `requirements.txt`
2. **Environment variables**: Verify all settings are configured in Application Settings
3. **Timeout errors**: Check function timeout settings (default: 5 minutes for Consumption plan)
4. **Authentication errors**: Verify API keys and endpoint URLs are correct

