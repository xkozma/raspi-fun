import speech_recognition as sr
import os
from dotenv import load_dotenv
import json

from gtts import gTTS
import playsound
from langchain.tools import Tool
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

def load_config():
    config_path = os.path.join(os.getcwd(),"python","assistant_config.json")
    default_config_path = os.path.join(os.getcwd(),"python", "default", "assistant_config_defaults.json")

    # Check if the configuration file exists
    if not os.path.exists(config_path):
        print(f"{config_path} not found. Creating with default settings.")
        # Load default settings
        with open(default_config_path, "r") as default_file:
            default_config = json.load(default_file)
        # Save default settings to the new config file
        with open(config_path, "w") as config_file:
            json.dump(default_config, config_file, indent=4)
    else:
        # Load existing configuration
        with open(config_path, "r") as config_file:
            default_config = json.load(config_file)

    return default_config

def load_localization_config():
    """Load the localization configuration"""
    config_path = os.path.join(os.getcwd(), "python", "default", "localization_config.json")
    with open(config_path, 'r') as file:
        return json.load(file)

def change_language(lang_code: str) -> str:
    """Change the assistant's language"""
    localization_config = load_localization_config()
    if lang_code not in localization_config['supported_languages']:
        return f"Language code {lang_code} is not supported. Available languages: {', '.join(localization_config['supported_languages'].keys())}"
    
    config_path = os.path.join(os.getcwd(), "python", "assistant_config.json")
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    config['language'] = lang_code
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
    
    return f"Language changed to {localization_config['supported_languages'][lang_code]} ({lang_code})"

# Define a custom tool to log messages
def log_message_tool(input_text: str) -> str:
    print(f"Log Tool: {input_text}")
    return f"Message logged: {input_text}"

log_tool = Tool(
    name="LogTool",
    func=log_message_tool,
    description="A tool to log messages to the console."
)

def order_pizza(details: str) -> str:
    """Simulate ordering a pizza"""
    print(f"🍕 Ordering pizza with details: {details}")
    return f"I've placed an order for your pizza with these details: {details}"

# Define tools
tools = [
    Tool(
        name="OrderPizza",
        func=order_pizza,
        description="Only use this tool when prompted to order a pizza and have all the details needed. Input should include toppings and size requirements, if not, ask for them in following question and then trigger this."
    ),
    Tool(
        name="ChangeLanguage",
        func=change_language,
        description="Changes the assistant's language. Input should be a language code (e.g., 'en-US', 'sk-SK')"
    )
]

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    load_dotenv()

    # Set up LangChain components
    llm = LangChainOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Get current language name
    localization_config = load_localization_config()
    config = load_config()
    current_language = localization_config['supported_languages'].get(config['language'], 'Unknown')
    
    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    print(f"Configuration loaded. Current language: {current_language} ({config['language']})")
    print("Listening for 'Hey Max'...")

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            transcript = recognizer.recognize_google(audio_data=audio, language=config['language']).lower()
            if "max" in transcript:
                print("You said:", transcript.strip())
                
                # Use the agent to process the request
                response = agent.run(
                    input=f"""You are a Voice Assistant named Max. You must respond ONLY in {current_language} language.
                    If the user asks about changing language, use the ChangeLanguage tool with the appropriate language code.
                    Current request: {transcript}"""
                )
                
                print("Assistant response:", response)
                
                # Convert the response to speech
                tts = gTTS(response, lang=config['language'][:2])
                temp_audio_path = os.path.join(os.getcwd(), "python", "temp", "response.mp3")
                os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
                tts.save(temp_audio_path)
                playsound.playsound(temp_audio_path)
                os.remove(temp_audio_path)
            
            else:
                print(transcript)

        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    main()
