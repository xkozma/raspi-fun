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
# Define tools
tools = [
    Tool(
        name="ChangeLanguage",
        func=change_language,
        description="Only triggers when user explicitly wants to change the language. Changes the assistant's language. Input should be a language code (e.g., 'en-US', 'sk-SK')"
    )
]

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    load_dotenv()

    # Initialize language manager
    lang_manager = LanguageManager()
    
    # Set up LangChain components
    llm = LangChainOpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    print(f"Configuration loaded. Current language: {lang_manager.current_language} ({lang_manager.get_language_code()})")
    print("Listening for 'Hey Max'...")

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
                print("You said:", transcript.strip())
                
                # Use the agent to process the request
                response = agent.run(
                    input=f"""You must respond ONLY in {lang_manager.current_language} language, you are a native speaker in that language. You are a Voice Assistant named Max.
                    User said this as speech to text, there can be mistakes: {transcript}"""
                )
                
                print("Assistant response:", response)
                
                # Convert the response to speech using current language
                tts = gTTS(response, lang=lang_manager.get_language_code()[:2])
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
