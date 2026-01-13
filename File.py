import RPi.GPIO as GPIO

import time

GPIO.setmode(GPIO.BCM)

Devices_main = {
}

for dev_name, dev_config in Devices_main.items():
    if dev_config['type'] == 'Output':
        GPIO.setup(dev_config['PIN'], GPIO.OUT)
    elif dev_config['type'] == 'Input':
        GPIO.setup(dev_config['PIN'], GPIO.IN)
    elif dev_config['type'] == 'Button':
        GPIO.setup(dev_config['PIN'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
Variables_main = {
}

GPIO.cleanup()
