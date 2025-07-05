import speech_recognition as sr
import os
from dotenv import load_dotenv
import json

from gtts import gTTS
import playsound

from language_manager import LanguageManager
from llm import stream_graph_updates, get_graph

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    load_dotenv()

    # Initialize language manager
    lang_manager = LanguageManager()
    
    # Initialize the GUI
    from gui.face_window import FaceWindow
    face_window = FaceWindow()
    
    # Set up LangChain agent
    graph = get_graph()

    print(f"Configuration loaded. Current language: {lang_manager.current_language} ({lang_manager.get_language_code()})")
    print("Listening for 'Hey Max'...")

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
                print("Transcript:", transcript.strip())
                if "max" in transcript:
                    face_window.set_listening(True)
                    print("You said:", transcript.strip())
                    input=f"""You must respond ONLY in {lang_manager.current_language} language, you are a native speaker in that language. You are a Voice Assistant named Max.
                        User said this as speech to text, there can be mistakes: {transcript}"""
                    # Use the agent to process the request
                    response = stream_graph_updates(graph, input)
                    
                    print("Assistant response:", response)
                    
                    # Convert the response to speech using current language
                    if response is not None:
                        tts = gTTS(response, lang=lang_manager.get_language_code()[:2])
                        temp_audio_path = os.path.join(os.getcwd(), "python", "temp", "response.mp3")
                        os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
                        tts.save(temp_audio_path)
                        playsound.playsound(temp_audio_path)
                        os.remove(temp_audio_path)
                        face_window.set_listening(False)
                
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
