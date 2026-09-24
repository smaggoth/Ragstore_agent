
import asyncio

from langchain_core.messages import SystemMessage

from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from brain.resources.tools import call_rag
from brain.resources.llm import llm, client
from brain.resources.profile import update_profile
from brain.resources.prompts import SYSTEM_PROMPT


async def build_graph():
    """Function that builds the graph of the agent"""
    web_search = await client.get_tools()
    tools = web_search + [call_rag]
    shorterm_memory = InMemorySaver()
    longterm_memory = InMemoryStore()

    def assistant(state:MessagesState):
        """main AI agent"""
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state['messages']
        response = llm.bind_tools(tools).invoke(messages)
        return {'messages': [response]}

    builder = StateGraph(MessagesState)
    builder.add_node('assistant', assistant)
    builder.add_node('update_profile', update_profile)
    builder.add_node('tools', ToolNode(tools))
    builder.add_edge(START, 'assistant')
    builder.add_conditional_edges(
        'assistant',
        tools_condition,
        {
            'tools':'tools',
            '__end__':'update_profile'
        })
    
    builder.add_edge('tools','assistant')
    builder.add_edge('update_profile', END)

    app = builder.compile(checkpointer=shorterm_memory, store=longterm_memory)
    return app


if __name__ == '__main__':
    #result = extractor.invoke({
    #    'messages':[{'role':'user', 'content':'Hola mi nombre es jorge trabajo como ingeniero de IA y tengo 31 años ademas soy baterista'}]
    #})
    #print(result['responses'][0])
    async def main():
        app = await build_graph()
        app.get_graph(xray=1).draw_mermaid_png(output_file_path="./grafo_output.png")
        config = {'configurable':{'thread_id':'jorge8a'}}
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'Busca en la base de conocimiento local cuál es el objetivo del proyecto'}]}, config)
        for m in result['messages']:
            m.pretty_print()

    asyncio.run(main())