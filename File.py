import RPi.GPIO as GPIO
import time
LED = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
while 4 >= 2:
    GPIO.output(LED, GPIO.LOW)
    time.sleep(3)
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(20)
time.sleep(3)
GPIO.cleanup()
