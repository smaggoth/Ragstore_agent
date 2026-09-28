from uuid import uuid4
from pydantic import BaseModel, Field

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from brain.resources.summarizer import State

class Memory(BaseModel):
    """An specific event or exchange within the conversation"""
    question: str = Field(description='The query or topic asked by the user')
    answer: str = Field(description='The answer from the agent or relevant information given')

embeddings = GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001')

longterm_memory = InMemoryStore(
    index={
        'embed':embeddings,
        'dims':3072,
        'fields':['question']
    }
)


def search_memories(query: str, thread_id: str, store: BaseStore, umbral: float = 0.85):
    """Search for relevant memories in the long term memory to answer repetitive questions without spend tokens"""
    namespace = ('memories', thread_id)
    result = store.search(namespace, query=query, limit=1)

    if result and result[0].score >= umbral:
        return result[0].value
    return None


def check_memory(state: State, config: RunnableConfig, store: BaseStore):
    """Search and find the memories if exist"""
    thread_id = config['configurable']['thread_id']
    last_question = state['messages'][-1].content

    memory_found = search_memories(last_question, thread_id, store)

    if memory_found:
        response = AIMessage(content=memory_found['answer'])
        return{'messages':[response]}
    return{}


def update_memory(state: State, config: RunnableConfig, store: BaseStore):
    """Function to update the long term memory"""
    thread_id = config['configurable']['thread_id']
    namespace = ('memories', thread_id)
    human_messages = [message for message in state['messages'] if isinstance(message, HumanMessage)]

    last_question = human_messages[-1].content #last Human message
    last_response = state['messages'][-1].content #last AI Message

    memory_id = str(uuid4())
    store.put(namespace, memory_id, {'question':last_question, 'answer':last_response})
    print(f'##DEBUG##MEMORY##GUARDADO:{store.get(namespace, memory_id)}')
    return {}


def route_after_memory_check(state: State):
    last_state_message = state['messages'][-1]
    if isinstance(last_state_message, AIMessage):
        return '__end__'
    return 'assistant'