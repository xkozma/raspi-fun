import speech_recognition as sr

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Listening for 'Hey Max'...")

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            transcript = recognizer.recognize_google(audio).lower()
            if "hey max" in transcript:
                print("You said:", transcript.replace("hey max", "").strip())
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

if __name__ == "__main__":
    main()
