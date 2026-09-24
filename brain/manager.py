import os
import asyncio
from dotenv import load_dotenv
from retrieval.search import search
from brain.resources.prompts import SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import tools_condition
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver


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

async def build_graph():

    web_search = await client.get_tools()
    tools = web_search + [call_rag]
    shorterm_memory = InMemorySaver()

    def assistant(state:MessagesState):

        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state['messages']
        response = llm.bind_tools(tools).invoke(messages)
        return {'messages': [response]}

    builder = StateGraph(MessagesState)
    builder.add_node('assistant', assistant)
    builder.add_node('tools', ToolNode(tools))
    builder.add_edge(START, 'assistant')
    builder.add_conditional_edges('assistant',tools_condition)
    builder.add_edge('tools', 'assistant')

    app = builder.compile(checkpointer=shorterm_memory)
    return app

if __name__ == '__main__':
    async def main():
        app = await build_graph()
        config = {'configurable':{'thread_id':'1'}}
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'Hola mi nombre es Jorge'}]}, config)
        for m in result['messages']:
            m.pretty_print()
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'y tengo 31 años'}]}, config)
        for m in result['messages']:
            m.pretty_print()
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'cual es mi nombre?'}]}, config)
        for m in result['messages']:
            m.pretty_print()
        config = {'configurable':{'thread_id':'2'}}
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'recuerdas mi nombre?'}]}, config)
        for m in result['messages']:
            m.pretty_print()
    asyncio.run(main())