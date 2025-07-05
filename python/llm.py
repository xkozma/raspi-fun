import os
import asyncio
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_openai import ChatOpenAI as LangChainOpenAI
from langchain.memory import ConversationBufferMemory

from tapo_light_control import turn_on_lights, turn_off_lights, get_light_info
from language_manager import change_language
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

def log_message_tool(input_text: str) -> str:
    print(f"Log Tool: {input_text}")
    return f"Message logged: {input_text}"

def turn_lights_on(_):
    return asyncio.run(turn_on_lights())

def turn_lights_off(_):
    return asyncio.run(turn_off_lights())

def get_lights_status(_):
    return asyncio.run(get_light_info())

def get_tools():
    return [
        Tool(
            name="ChangeLanguage",
            func=change_language,
            description="Only triggers when user explicitly wants to change the language. Changes the assistant's language. Input should be a language code (e.g., 'en-US', 'sk-SK')"
        ),
        Tool(
            name="TurnLightsOn",
            func=turn_lights_on,
            description="Turns on the Tapo smart lights"
        ),
        Tool(
            name="TurnLightsOff",
            func=turn_lights_off,
            description="Turns off the Tapo smart lights"
        ),
        Tool(
            name="GetLightsStatus",
            func=get_lights_status,
            description="Gets the current status of the Tapo smart lights"
        ),
        Tool(
            name="LogTool",
            func=log_message_tool,
            description="A tool to log messages to the console."
        )
    ]

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def get_graph():
    load_dotenv()
    llm = LangChainOpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    def agent(state: State):
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def tool_router(state: State):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END
    tool_node = ToolNode(tools)
    builder = StateGraph(State)

    builder.add_node("agent", agent)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tool_router, ["tools", END])
    builder.add_edge("tools", "agent")
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph

def stream_graph_updates(graph, user_input: str):
    for event in graph.stream(
        {"messages": [("user", user_input)]},
        # the thread must be specified when initialising the state
        {"configurable": {"thread_id": "1"}},
    ):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
            if value["messages"][-1].content != '':
                return value["messages"][-1].content