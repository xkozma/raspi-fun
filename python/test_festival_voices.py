import subprocess
import os

def list_festival_voices():
    """List all available Festival voices"""
    try:
        # Get list of voices using festival command
        cmd = "echo '(voice.list)' | festival"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("Available Festival voices:")
        print(result.stdout)
        return result.stdout.strip().split('\n')
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []

def test_voice(voice_name, text="Hello, this is a test of the Festival voice system"):
    """Test a specific Festival voice"""
    try:
        # Create a temporary script file
        script = f"""(voice_{voice_name})
(SayText "{text}")"""
        
        with open("/tmp/festival_test.scm", "w") as f:
            f.write(script)
        
        # Run the test
        print(f"\nTesting voice: {voice_name}")
        subprocess.run(["festival", "-b", "/tmp/festival_test.scm"])
        
    except Exception as e:
        print(f"Error testing voice {voice_name}: {e}")

def main():
    # List all voices
    voices = list_festival_voices()
    
    # Test each voice
    test_text = "Hello, I am Max, your voice assistant."
    for voice in voices:
        voice = voice.strip()
        if voice:
            test_voice(voice, test_text)
            input("Press Enter to test next voice...")

if __name__ == "__main__":
    main()
