import subprocess

def test_festival():
    # Test if festival is installed
    try:
        result = subprocess.run(["which", "festival"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Festival is not installed. Please install it using:")
            print("sudo apt-get install festival festival-freebsoft-utils")
            return
        
        print("Festival is installed")
        
        # Test voice list
        print("\nTesting voice list:")
        result = subprocess.run("echo '(voice.list)' | festival", 
                              shell=True, capture_output=True, text=True)
        print(result.stdout)
        
        # Test basic TTS
        print("\nTesting basic TTS:")
        subprocess.run("echo 'This is a test of Festival text to speech' | festival --tts", shell=True)
        
    except Exception as e:
        print(f"Error testing Festival: {e}")

if __name__ == "__main__":
    test_festival()
