from langchain.tools import tool
from retrieval.search import search

@tool
def call_rag(query: str) -> list:
    """Tool that search for the information requested by the user in a local RAG store when data is not available in the web"""
    response = search(query)
    current_response = [
       text.lstrip("#\n")
        for item in response.values()
        if (text := item.get("payload", {}).get("text"))
        ]
    return ["\n".join(current_response)]