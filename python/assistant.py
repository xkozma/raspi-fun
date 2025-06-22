import speech_recognition as sr
import os
import openai
from dotenv import load_dotenv

from openai import OpenAI
from datetime import datetime
from gtts import gTTS
import tempfile
import playsound

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve OpenAI API key from environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    print("Listening for 'Hey Max'...")
    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            transcript = recognizer.recognize_google(audio).lower()
            if "hey max" in transcript:
                print("You said:", transcript.replace("hey max", "").strip())
                print("Assistant script executed")
                now = datetime.now()
                date_time_sentence = f"!Next part is automatic include, just for your information, not from user, do not use it if not necessary: ###It's {now.strftime('%A, %B %d, %Y')} today.### Never use emojis. Respons like a voice assistant, so your responses are quick and to the point. Never include your sources of information. Respond in one, maximum of two sentences."
                transcript += f" {date_time_sentence}"
                # Send the transcript to OpenAI LLM
                response = client.responses.create(
                    model="gpt-4.1",
                    tools=[{"type": "web_search_preview"}],
                    input=transcript,
                    max_output_tokens=50,
                )

                try:
                    response_text = response.output[0].content[0].text.strip()
                except (IndexError, AttributeError):
                    try:
                        response_text = response.output[1].content[0].text.strip()
                    except (IndexError, AttributeError):
                        response_text = "Unable to retrieve a valid response from OpenAI."

                response_text = response_text.replace(",", "")
                print(response_text)

                # Convert the response text to speech
                tts = gTTS(response_text, lang='en')
                temp_audio_path = os.path.join(os.getcwd(), "temp", "response.mp3")
                os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
                tts.save(temp_audio_path)
                print(f"Response saved to {temp_audio_path}")
                playsound.playsound(temp_audio_path)
                os.remove(temp_audio_path)

            else:
                print(transcript)
                # ...future implementation for assistant functionality...
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    main()
print("Assistant script executed")
