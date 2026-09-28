
import asyncio

from langchain_core.messages import SystemMessage
from langchain_core.runnables.config import RunnableConfig

from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore


from brain.resources.tools import call_rag
from brain.resources.llm import llm, client
from brain.resources.profile import update_profile
from brain.resources.prompts import SYSTEM_PROMPT
from brain.resources.memory import check_memory, update_memory, route_after_memory_check, longterm_memory
from brain.resources.summarizer import summarize_conversation, summary_trigger, State

async def build_graph():
    """Function that builds the graph of the agent"""
    web_search = await client.get_tools()
    tools = web_search + [call_rag]
    shorterm_memory = InMemorySaver()

    def assistant(state: State, config: RunnableConfig, store: BaseStore):
        """main AI agent"""
        thread_id = config['configurable']['thread_id']
        namespace = ('profile', thread_id)
        profile_item = store.get(namespace, 'profile_data')
        profile_context = f'\n\nKnown user information: {profile_item}' if profile_item else ''

        summary = state.get('summary', '')
        print(f'##DEBUG##: SUMMARY ACTUAL:{summary}')

        system_content = SYSTEM_PROMPT + profile_context
        if summary:
            system_content + f'\n\nSummary of previous conversation: {summary}'
        
        messages = [SystemMessage(content=system_content)] + state['messages']
        response = llm.bind_tools(tools).invoke(messages)
        return {'messages': [response]}

    builder = StateGraph(State)
    builder.add_node('check_memory', check_memory)
    builder.add_node('assistant', assistant)
    builder.add_node('update_profile', update_profile)
    builder.add_node('update_memory', update_memory)
    builder.add_node('tools', ToolNode(tools))
    builder.add_node('summarize_conversation', summarize_conversation)

    builder.add_edge(START, 'check_memory')
    builder.add_conditional_edges(
        'check_memory', 
        route_after_memory_check,
        {
            'assistant': 'assistant',
            '__end__': 'update_profile'
            })
    builder.add_conditional_edges(
        'assistant',
        tools_condition,
        {
            'tools':'tools',
            '__end__':'update_memory'
        })
    builder.add_edge('update_memory', 'update_profile')
    builder.add_edge('tools','assistant')
    builder.add_conditional_edges(
        'update_profile',
        summary_trigger,
        {
            'summarize_conversation': 'summarize_conversation',
            '__end__': END
        }
    )
    builder.add_edge('summarize_conversation', END)

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
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'Hola mi nombre es Jorge, soy ingeniero y acabo de cumplir 31 años'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'cual es la 3 fase de mi proyecto RAG?'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'recuerdas mi edad?'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'Ya casi termino el agente con Langgraph del proyecto'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'que es un loro estocastico? resumelo en 4 lineas'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'Mi proyecto RAG involucra un loro estocastico?'}]}, config)
        result = await app.ainvoke({'messages':[{'role':'user', 'content':'recuerdas que tengo 31 años, los cumpli hace casi un mes, el 26 de agosto'}]}, config)
        for m in result['messages']:
            m.pretty_print()

    asyncio.run(main())