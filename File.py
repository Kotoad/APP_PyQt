from machine import Pin
import time
Devices = {
    "DEV":{"PIN": 8, "type":"Output"},
}
Variables = {
    "VAR":{"value": 5},
}
for dev_name, dev_config in Devices.items():
    if dev_config['type'] == 'Output':
        dev_name = Pin(dev_config['PIN'], Pin.OUT)
    elif dev_config['type'] == 'Input':
        dev_name = Pin(dev_config['PIN'], Pin.IN)
while Variables['VAR']['value'] == 5:
    Devices['DEV']['PIN'].value(0)
    time.sleep(2)
    time.sleep(50)
    Devices['DEV']['PIN'].value(1)
time.sleep(20)
