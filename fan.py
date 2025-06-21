import RPi.GPIO as GPIO
import time

# Pin configuration
FAN_PIN = 16  # Replace with the GPIO pin you're using

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Turn the fan on
GPIO.output(FAN_PIN, GPIO.HIGH)
time.sleep(10)  # Keep the fan on for 10 seconds

# Turn the fan off
GPIO.output(FAN_PIN, GPIO.LOW)

# Cleanup
GPIO.cleanup()