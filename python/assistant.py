import speech_recognition as sr
import os
from dotenv import load_dotenv
import json
from typing import TypedDict, List, Dict, Any

from gtts import gTTS
import playsound
from langchain.tools import Tool
from langchain_openai import OpenAI as LangChainOpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType, create_react_agent
from langchain.memory import ConversationBufferMemory
import asyncio
from tapo_light_control import turn_on_lights, turn_off_lights, get_light_info

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

from langgraph.graph import StateGraph, END

class LanguageManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.config = self.load_config()
        self.localization_config = self.load_localization_config()
        self.current_language = self.get_current_language()
    
    def load_config(self):
        config_path = os.path.join(os.getcwd(),"python","assistant_config.json")
        default_config_path = os.path.join(os.getcwd(),"python", "default", "assistant_config_defaults.json")

        if not os.path.exists(config_path):
            print(f"{config_path} not found. Creating with default settings.")
            with open(default_config_path, "r") as default_file:
                config = json.load(default_file)
            with open(config_path, "w") as config_file:
                json.dump(config, config_file, indent=4)
        else:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
        return config

    def load_localization_config(self):
        config_path = os.path.join(os.getcwd(), "python", "default", "localization_config.json")
        with open(config_path, 'r') as file:
            return json.load(file)
    
    def get_current_language(self):
        return self.localization_config['supported_languages'].get(self.config['language'], 'Unknown')
    
    def get_language_code(self):
        return self.config['language']
    
    def set_language(self, lang_code: str) -> str:
        if lang_code not in self.localization_config['supported_languages']:
            return f"Language code {lang_code} is not supported. Available languages: {', '.join(self.localization_config['supported_languages'].values())}"
        
        config_path = os.path.join(os.getcwd(), "python", "assistant_config.json")
        self.config['language'] = lang_code
        with open(config_path, 'w') as file:
            json.dump(self.config, file, indent=4)
        
        self.current_language = self.get_current_language()
        return f"Language changed to {self.current_language}, please respond in {self.current_language} language now."

# Update the change_language tool to use LanguageManager
def change_language(lang_code: str) -> str:
    return LanguageManager().set_language(lang_code)

# Define a custom tool to log messages
def log_message_tool(input_text: str) -> str:
    print(f"Log Tool: {input_text}")
    return f"Message logged: {input_text}"

log_tool = Tool(
    name="LogTool",
    func=log_message_tool,
    description="A tool to log messages to the console."
)

# Define wrapper functions for async tools
def turn_lights_on(_):
    return asyncio.run(turn_on_lights())

def turn_lights_off(_):
    return asyncio.run(turn_off_lights())

def get_lights_status(_):
    return asyncio.run(get_light_info())

# Update tools list before agent initialization
tools = [
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
    )
]

# 1. Define the agent state
class AgentState(TypedDict):
    input: str
    chat_history: List[Dict[str, Any]]
    agent_outcome: Any
    steps: List[List[str]]

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    load_dotenv()

    # Initialize language manager
    lang_manager = LanguageManager()
    
    # Initialize the GUI
    from gui.face_window import FaceWindow
    face_window = FaceWindow()
    
    # Set up LangChain components
    # llm = LangChainOpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # 2. Create the LLM
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))

    # 4. Define the agent logic
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful voice assistant named Max. You can perform various tasks such as controlling smart lights, changing languages, and responding to user queries. Use the tools provided to assist the user effectively."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    llm_with_tools = llm.bind(functions=[tool.to_tool_schema() for tool in tools])

    def get_response(state):
        messages = prompt.format_messages(
            input=state['input'],
            chat_history=state['chat_history'],
            agent_scratchpad=format_to_openai_function_messages(state['steps'])
        )
        return llm_with_tools.invoke(messages)

    # 5. Define the graph nodes
    def should_continue(state):
        if state['agent_outcome'].tool is not None:
            return "continue"
        else:
            return "end"

    def call_tool(state):
        action = state['agent_outcome']
        tool_name = action.tool
        tool_input = action.tool_input
        
        # Find the tool function and execute it
        tool = next((tool for tool in tools if tool.name == tool_name), None)
        if tool:
            return tool.func(tool_input)
        else:
            return f"Tool {tool_name} not found."

    def update_history(state):
        chat_history = state['chat_history']
        input = state['input']
        agent_outcome = state['agent_outcome']

        chat_history.append({"role": "user", "content": input})
        chat_history.append({"role": "assistant", "content": agent_outcome.content})

        return {"chat_history": chat_history}

    # 6. Create the graph
    builder = StateGraph(AgentState)
    builder.add_node("agent", get_response)
    builder.add_node("tool", call_tool)
    builder.add_node("update_history", update_history)

    builder.set_entry_point("agent")

    builder.add_edge("agent", "tool", condition=should_continue)
    builder.add_edge("agent", END, condition=should_continue)
    builder.add_edge("tool", "update_history")
    builder.add_edge("update_history", "agent")

    # 7. Compile the graph
    graph = builder.compile()

    # Initialize the agent
    # agent = create_react_agent(
    #     tools=tools,
    #     llm=llm,
    #     prompt="You are a helpful voice assistant named Max. You can perform various tasks such as controlling smart lights, changing languages, and responding to user queries. Use the tools provided to assist the user effectively.",
    # )

    print(f"Configuration loaded. Current language: {lang_manager.current_language} ({lang_manager.get_language_code()})")
    print("Listening for 'Hey Max'...")

    chat_history = []

    try:
        while True:
            try:
                with microphone as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)

                transcript = recognizer.recognize_google(
                    audio_data=audio, 
                    language=lang_manager.get_language_code()
                ).lower()

                if "max" in transcript:
                    face_window.set_listening(True)
                    print("You said:", transcript.strip())
                    
                    # Use the agent to process the request
                    # response = agent.run(
                    #     input=f"""You must respond ONLY in {lang_manager.current_language} language, you are a native speaker in that language. You are a Voice Assistant named Max.
                    #     User said this as speech to text, there can be mistakes: {transcript}"""
                    # )

                    # 8. Use the Langgraph agent
                    inputs = {"input": transcript, "chat_history": chat_history, "steps": []}
                    response = graph.invoke(inputs)
                    
                    print("Assistant response:", response['agent_outcome'].content)
                    
                    # Convert the response to speech using current language
                    tts = gTTS(response['agent_outcome'].content, lang=lang_manager.get_language_code()[:2])
                    temp_audio_path = os.path.join(os.getcwd(), "python", "temp", "response.mp3")
                    os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
                    tts.save(temp_audio_path)
                    playsound.playsound(temp_audio_path)
                    os.remove(temp_audio_path)
                    face_window.set_listening(False)

                    chat_history.append({"role": "user", "content": transcript})
                    chat_history.append({"role": "assistant", "content": response['agent_outcome'].content})
                
                else:
                    print(transcript)

            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

    except KeyboardInterrupt:
        face_window.close()

if __name__ == "__main__":
    main()
