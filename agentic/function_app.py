import logging
import os
import azure.functions as func
import json
from dotenv import load_dotenv
from knowledgebase_service import KnowledgeBaseService

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the service (will use environment variables)
kb_service = None

def get_kb_service():
    """Lazy initialization of the knowledge base service."""
    global kb_service
    if kb_service is None:
        logger.info("Initializing KnowledgeBaseService")
        kb_service = KnowledgeBaseService()
    return kb_service


app = func.FunctionApp()


@app.function_name(name="KnowledgeBaseRetrieval")
@app.route(route="knowledgebase", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def knowledgebase_retrieval(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to retrieve information from the knowledge base.
    
    Expected request body (JSON):
    {
        "assistant_message": "The assistant/system message",
        "user_message": "The user's query message",
        "include_references": true,  // optional, default: true
        "include_reference_source_data": true,  // optional, default: true
        "always_query_source": false,  // optional, default: false
        "include_activity": true  // optional, default: true
    }
    """
    try:
        logger.info("KnowledgeBaseRetrieval function triggered")
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            logger.error("Invalid JSON in request body")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        if not req_body:
            logger.error("Empty request body")
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        assistant_message = req_body.get("assistant_message")
        user_message = req_body.get("user_message")
        
        if not assistant_message or not user_message:
            logger.error("Missing required fields: assistant_message or user_message")
            return func.HttpResponse(
                json.dumps({"error": "Both 'assistant_message' and 'user_message' are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get optional parameters
        include_references = req_body.get("include_references", True)
        include_reference_source_data = req_body.get("include_reference_source_data", True)
        always_query_source = req_body.get("always_query_source", False)
        include_activity = req_body.get("include_activity", True)
        
        logger.info("Calling knowledge base service")
        # Retrieve from knowledge base
        service = get_kb_service()
        response_text = service.retrieve(
            assistant_message=assistant_message,
            user_message=user_message,
            include_references=include_references,
            include_reference_source_data=include_reference_source_data,
            always_query_source=always_query_source,
            include_activity=include_activity
        )
        
        logger.info("Successfully retrieved response from knowledge base")
        
        # Return response
        return func.HttpResponse(
            json.dumps({
                "success": True,
                "response": response_text
            }),
            status_code=200,
            mimetype="application/json"
        )
        
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Configuration error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

