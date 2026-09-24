import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite',
    google_api_key = os.getenv("GEMINI_API_KEY")
)


client = MultiServerMCPClient(
    {
        'local_server':{
            'transport': 'stdio',
            'command': 'python',
            'args': ['brain/resources/web_mcp_server.py'],
        }
    }
)