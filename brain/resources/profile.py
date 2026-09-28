from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig

from langgraph.store.base import BaseStore
from trustcall import create_extractor

from brain.resources.llm import llm
from brain.resources.summarizer import State


class Profile(BaseModel):
    """Stable information from user"""
    name: Optional[str] = Field(default=None, description='Name of the user')
    age:  Optional[int] = Field(default=None, description='Age of the user')
    role: Optional[str] = Field(default=None, description='User role or occupation')

extractor = create_extractor(
    llm,
    tools=[Profile],
    tool_choice='Profile',
)


def update_profile(state: State, config: RunnableConfig, store: BaseStore):
    """Function to update the user profile with information extracted by TrustCall"""
    thread_id = config['configurable']['thread_id']
    namespace = ('profile', thread_id)
    human_messages = [message for message in state['messages'] if isinstance(message, HumanMessage)]

    existing_item = store.get(namespace, 'profile_data')
    existing_profile = {'Profile': existing_item.value} if existing_item else None

    result = extractor.invoke({
        'messages': human_messages,
        'existing': existing_profile,
    })

    updated_profile = result['responses'][0].model_dump()
    store.put(namespace, 'profile_data', updated_profile)
    print(f'##DEBUG##PERFIL#ACTUAL:{store.get(namespace,'profile_data')}')
    return{}