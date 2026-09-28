from langgraph.graph import MessagesState
from langchain_core.messages import RemoveMessage, HumanMessage
from brain.resources.prompts import NEW_SUMMARY, CONTINUE_SUMMARY
from brain.resources.llm import llm

class State(MessagesState):
    summary: str

def summarize_conversation(state: State):
    print(f'DEBUG##: SUMMARY TRIGGERED LEN: {len(state['messages'])}')
    summary = state.get('summary', "")

    if summary:
        summary_prompt = CONTINUE_SUMMARY
    else: 
        summary_prompt = NEW_SUMMARY
    messages = state['messages'] + [HumanMessage(summary_prompt)]
    response = llm.invoke(messages)
    delete_messages = [RemoveMessage(id=msg.id) for msg in state['messages'][:-1]]
    print(f'##DEBUG##SUMMARY UPDATED##: {response}')
    return{'summary':response, 'messages':delete_messages}

def summary_trigger(state: State):
    if len(state['messages']) > 5:
        return 'summarize_conversation'
    return '__end__'

