import speech_recognition as sr
import os
from dotenv import load_dotenv
import json
import pyttsx3
import playsound
from langchain.tools import Tool
from langchain_openai import OpenAI as LangChainOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
import asyncio
from tapo_light_control import turn_on_lights, turn_off_lights, get_light_info
from vosk import Model, KaldiRecognizer
import pyaudio

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

class TTSManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.voice_map = self._create_voice_map()
        
    def _create_voice_map(self):
        # Map language codes to available system voices
        voice_map = {}
        for voice in self.voices:
            lang_code = voice.languages[0] if voice.languages else ''
            # Store both full language code and short version
            voice_map[lang_code] = voice.id
            if '-' in lang_code:
                short_code = lang_code.split('-')[0]
                voice_map[short_code] = voice.id
        return voice_map
    
    def speak(self, text: str, lang_code: str):
        # Get the short language code (e.g., 'en' from 'en-US')
        short_lang = lang_code[:2] if '-' in lang_code else lang_code
        
        # Try to find appropriate voice
        voice_id = self.voice_map.get(lang_code) or self.voice_map.get(short_lang)
        
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        
        self.engine.say(text)
        self.engine.runAndWait()

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

def setup_vosk():
    # Make sure to download a model from https://alphacephei.com/vosk/models
    # and place it in a 'model' directory
    model_path = os.path.join(os.getcwd(), "python", "model")
    if not os.path.exists(model_path):
        raise RuntimeError("Please download a Vosk model and place it in the 'python/model' directory")
    return Model(model_path)

def main():
    load_dotenv()
    
    # Initialize Vosk
    model = setup_vosk()
    
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=16000,
                   input=True,
                   frames_per_buffer=8000)
    stream.start_stream()
    
    # Initialize Vosk recognizer
    recognizer = KaldiRecognizer(model, 16000)

    # Initialize language manager
    lang_manager = LanguageManager()
    
    # Initialize the GUI
    from gui.face_window import FaceWindow
    face_window = FaceWindow()
    
    # Set up LangChain components
    llm = LangChainOpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory
    )

    # Initialize TTS
    tts_manager = TTSManager()

    print(f"Configuration loaded. Current language: {lang_manager.current_language} ({lang_manager.get_language_code()})")
    print("Listening for 'Hey Max'...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if result.get("text", ""):
                    transcript = result["text"].lower()
                    print("Recognized:", transcript)

                    if "max" in transcript:
                        face_window.set_listening(True)
                        print("You said:", transcript.strip())
                        
                        # Use the agent to process the request
                        response = agent.run(
                            input=f"""You must respond ONLY in {lang_manager.current_language} language, you are a native speaker in that language. You are a Voice Assistant named Max.
                            User said this as speech to text, there can be mistakes: {transcript}"""
                        )
                        
                        print("Assistant response:", response)
                        
                        # Replace gTTS with pyttsx3
                        tts_manager.speak(response, lang_manager.get_language_code())
                        face_window.set_listening(False)

    except KeyboardInterrupt:
        face_window.close()
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
