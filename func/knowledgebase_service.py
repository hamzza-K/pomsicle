import os
import logging
from typing import Optional, List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import (
    SearchIndexKnowledgeSourceParams,
    KnowledgeBaseRetrievalRequest,
    KnowledgeBaseMessage,
    KnowledgeBaseMessageTextContent
)

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service class for interacting with Azure Cognitive Search Knowledge Base."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        knowledge_base_name: Optional[str] = None,
        knowledge_source_name: Optional[str] = None
    ):
        """
        Initialize the Knowledge Base Service.
        
        Args:
            endpoint: Azure Search endpoint URL. If not provided, reads from AZURE_SEARCH_ENDPOINT env var.
            api_key: Azure Search API key. If not provided, reads from AZURE_SEARCH_API_KEY env var.
            knowledge_base_name: Knowledge base name. If not provided, reads from KB_NAME env var.
            knowledge_source_name: Knowledge source name. If not provided, reads from KB_SOURCE_NAME env var.
        """
        self.endpoint = endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_SEARCH_API_KEY")
        self.knowledge_base_name = knowledge_base_name or os.getenv("KB_NAME", "knowledgebase-phases")
        self.knowledge_source_name = knowledge_source_name or os.getenv("KB_SOURCE_NAME", "knowledgesource-phases")
        
        if not self.endpoint:
            raise ValueError("Azure Search endpoint is required. Set AZURE_SEARCH_ENDPOINT environment variable.")
        if not self.api_key:
            raise ValueError("Azure Search API key is required. Set AZURE_SEARCH_API_KEY environment variable.")
        
        logger.info(f"Initializing KnowledgeBaseService with endpoint: {self.endpoint}")
        logger.info(f"Knowledge base: {self.knowledge_base_name}, Source: {self.knowledge_source_name}")
        
        self.client = KnowledgeBaseRetrievalClient(
            endpoint=self.endpoint,
            knowledge_base_name=self.knowledge_base_name,
            credential=AzureKeyCredential(self.api_key)
        )
        logger.info("KnowledgeBaseRetrievalClient initialized successfully")
    
    def retrieve(
        self,
        assistant_message: str,
        user_message: str,
        include_references: bool = True,
        include_reference_source_data: bool = True,
        always_query_source: bool = False,
        include_activity: bool = True
    ) -> str:
        """
        Retrieve information from the knowledge base.
        
        Args:
            assistant_message: The assistant/system message to provide context.
            user_message: The user's query message.
            include_references: Whether to include references in the response.
            include_reference_source_data: Whether to include source data in references.
            always_query_source: Whether to always query the source.
            include_activity: Whether to include activity information.
        
        Returns:
            The text content from the knowledge base response.
        """
        try:
            logger.info("Creating knowledge base retrieval request")
            logger.debug(f"Assistant message: {assistant_message[:100]}...")
            logger.debug(f"User message: {user_message[:100]}...")
            
            request = KnowledgeBaseRetrievalRequest(
                messages=[
                    KnowledgeBaseMessage(
                        role="assistant",
                        content=[KnowledgeBaseMessageTextContent(text=assistant_message)]
                    ),
                    KnowledgeBaseMessage(
                        role="user",
                        content=[KnowledgeBaseMessageTextContent(text=user_message)]
                    ),
                ],
                knowledge_source_params=[
                    SearchIndexKnowledgeSourceParams(
                        knowledge_source_name=self.knowledge_source_name,
                        include_references=include_references,
                        include_reference_source_data=include_reference_source_data,
                        always_query_source=always_query_source,
                    )
                ],
                include_activity=include_activity,
            )
            
            logger.info("Sending retrieval request to knowledge base")
            result = self.client.retrieve(request)
            
            if not result.response or len(result.response) == 0:
                logger.warning("Empty response received from knowledge base")
                return ""
            
            if not result.response[0].content or len(result.response[0].content) == 0:
                logger.warning("Empty content in knowledge base response")
                return ""
            
            response_text = result.response[0].content[0].text
            logger.info(f"Successfully retrieved response (length: {len(response_text)} characters)")
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error retrieving from knowledge base: {str(e)}", exc_info=True)
            raise

