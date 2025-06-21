import RPi.GPIO as GPIO

# Pin configuration
FAN_PIN = 16  # Replace with the GPIO pin you're using

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

try:
    # Turn the fan on continuously
    GPIO.output(FAN_PIN, GPIO.HIGH)
    print("Fan is running. Press Ctrl+C to stop.")
    while True:
        pass  # Keep the program running
except KeyboardInterrupt:
    # Handle user interruption (Ctrl+C)
    print("Stopping the fan...")
finally:
    # Turn the fan off and cleanup
    GPIO.output(FAN_PIN, GPIO.LOW)
    GPIO.cleanup()