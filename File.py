import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
Devices = {
    "DEV":{"PIN": 17, "type":"Output"},
}
for dev_name, dev_config in Devices.items():
    if dev_config['type'] == 'Output':
        GPIO.setup(dev_config['PIN'], GPIO.OUT)
    elif dev_config['type'] == 'Input':
        GPIO.setup(dev_config['PIN'], GPIO.IN)
Variables = {
    "var":{"value": 1},
}
while Variables['var']['value'] == Variables['var']['value']:
    time.sleep(1000/1000)
    GPIO.output(Devices['DEV']['PIN'], GPIO.HIGH)
    time.sleep(1000/1000)
    GPIO.output(Devices['DEV']['PIN'], GPIO.LOW)
GPIO.cleanup()
