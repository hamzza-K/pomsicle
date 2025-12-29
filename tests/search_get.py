from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import json

service_endpoint = "https://ask-poms.search.windows.net"
index_name = "search-phases"
api_key = "3QZj3DVGel2YOU2KlTvZdpat8nOgZbkoxLWu6Hv3ogAzSeABpIyJ"


search_client = SearchClient(
    endpoint=service_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(api_key)
)

results = search_client.search(
    search_text="display the information to users and prompt them to make a choice.`",
    query_type="semantic",
    top=5
)

for result in results:
    score = result["@search.score"]
    content = json.loads(result["content"])
    print(f"{score:.3f} | {content['id']} | {content['description']}")