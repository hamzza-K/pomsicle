from azure.core.credentials import AzureKeyCredential
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
from azure.search.documents.knowledgebases.models import SearchIndexKnowledgeSourceParams, KnowledgeBaseRetrievalRequest, KnowledgeBaseMessage, KnowledgeBaseMessageTextContent
import dotenv

dotenv.load_dotenv()

endpoint = dotenv.get_key(dotenv.find_dotenv(), "AZURE_KB_ENDPOINT") or "https://ask-poms.search.windows.net"
knowledge_base_name = dotenv.get_key(dotenv.find_dotenv(), "AZURE_KB_NAME")
credential = dotenv.get_key(dotenv.find_dotenv(), "AZURE_KB_CREDENTIAL")

kb_client = KnowledgeBaseRetrievalClient(endpoint = endpoint, knowledge_base_name = knowledge_base_name, credential = AzureKeyCredential(credential))

request = KnowledgeBaseRetrievalRequest(
    messages=[
        KnowledgeBaseMessage(
            role = "assistant",
            content = [KnowledgeBaseMessageTextContent(text = "The name of the phases are usually the file names, only return those names. Finally append a list of phases to be added.")]
        ),
        KnowledgeBaseMessage(
            role = "user",
            content = [KnowledgeBaseMessageTextContent(text = "Give me your analysis and best suited phases to create the recipe with the following requirements: Asks operators if they have read the instructions before starting the operation, choices should be given to the operators. After confirming that, the starting time should be noted and the operator starts testing the vials. After each test the operator also weighs individual vials if the weigh is outside the bounds of the given weight requirement then the operator should note down that vial and continue testing the others. After the testing is complete, the failed vials and the total vials should be shown in a table. At the end the end time should be noted.")]
        ),
    ],
    knowledge_source_params=[
        SearchIndexKnowledgeSourceParams(
            knowledge_source_name = "knowledgesource-phases",
            include_references = True,
            include_reference_source_data = True,
            always_query_source = False,
        )
    ],
    include_activity = True,
)

result = kb_client.retrieve(request)
print(result.response[0].content[0].text)