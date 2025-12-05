import RPi.GPIO as GPIO
import time
LED = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
while 2 == 2:
    GPIO.output(LED, GPIO.LOW)
    time.sleep(2)
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(3)
time.sleep(20)
GPIO.cleanup()
