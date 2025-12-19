import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
Devices = {
    "LED":{"PIN": 17, "type":"Output"},
}
for dev_name, dev_config in Devices.items():
    if dev_config['type'] == 'Output':
        GPIO.setup(dev_config['PIN'], GPIO.OUT)
    elif dev_config['type'] == 'Input':
        GPIO.setup(dev_config['PIN'], GPIO.IN)
    elif dev_config['type'] == 'Button':
        GPIO.setup(dev_config['PIN'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
Variables = {
}
while True:
    GPIO.output(Devices['LED']['PIN'], GPIO.HIGH)
    time.sleep(1000/1000)
    GPIO.output(Devices['LED']['PIN'], GPIO.LOW)
    time.sleep(1000/1000)
GPIO.cleanup()
