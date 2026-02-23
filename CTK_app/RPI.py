import RPi.GPIO as GPIO
import time

# Setup
LED_PIN = 17
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(LED_PIN, GPIO.OUT)

# Blink LED
try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
        time.sleep(1)
        GPIO.output(LED_PIN, GPIO.LOW)   # Turn LED off
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup() 