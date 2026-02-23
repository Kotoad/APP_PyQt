import asyncio
from microdot import Microdot, send_file
from microdot.websocket import with_websocket
import network
import socket
from time import sleep
import machine
import rp2
import sys

ssid = 'name-rsoc'
password = 'idk123456'

MOT1_PIN = [10, 11]
MOT2_PIN = [12, 13]
motor1 = Pin(MOT1_PIN[0], Pin.OUT)
motor1_pwm = PWM(Pin(MOT1_PIN[1]), freq=2000)
motor2 = Pin(MOT2_PIN[0], Pin.OUT)
motor2_pwm = PWM(Pin(MOT2_PIN[1]), freq=2000)

async def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        await asyncio.sleep(1)

    print(wlan.ifconfig())

async def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

app = Microdot()

@app.route('/')
async def index(request):
    try:
        #file_path = os.path.join(os.path.dirname(__file__), 'index.html')
        return send_file('index.html')
    except Exception as e:
        #logging.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

@app.route('/prijem')
@with_websocket
async def prijem(request, ws):
    #global command, smer, rychlost
    try:
        while True:
            prijem = await ws.receive()
            #logging.debug(f"Received message: {prijem}")
            parts = prijem.split()
            #print(parts)
            command = parts[0]
            smer = int(parts[1])
            rychlost = int((int(parts[2])/100)*65535)
            
            pohyb(command, smer, rychlost)
            
    except Exception as e:
        #logging.error(f"Error in prijem route: {e}")
        pass

def pohyb(command, smer, rychlost):
    def vpred(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
            motor1.duty_u16(rychlost)
            motor2.duty_u16(rychlost)
    
    def vzad(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")

    
    def v_pravo(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")
    
    def v_levo(command, rychlost):
        if command == 'start':
            print(f"Směr: {smer}")
            print(f"Rychlost: {rychlost}")

    def stop():
        print("stop")

    if smer == 1:
        vpred(command, rychlost)
    elif smer == 2:
        vzad(command, rychlost)
    elif smer == 3:
        v_pravo(command, rychlost)
    elif smer == 4:
        v_levo(command, rychlost)
    elif smer == 0:
        stop()

async def main():

    #await connect()
    await ap_mode(ssid, password)
    # start the server in a background task
    server = asyncio.create_task(app.start_server())

    # ... do other asynchronous work here ...

    # cleanup before ending the application
    await server

asyncio.run(main())
