import os
import asyncio
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

from tapo_light_control import turn_on_lights, turn_off_lights, get_light_info
from language_manager import change_language

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

def get_agent(lang_manager):
    load_dotenv()
    llm = LangChainOpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    tools = get_tools()
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )
    return agent
