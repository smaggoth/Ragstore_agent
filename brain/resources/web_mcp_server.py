from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from typing import Dict

load_dotenv()

mcp = FastMCP('mcp_server')

tavily_client = TavilyClient()

@mcp.tool()
def web_search(query: str) -> Dict:
    """Search in the web for the information requested by the user"""
    response = tavily_client.search(query)
    return response

if __name__ == '__main__':
    mcp.run(transport='stdio')