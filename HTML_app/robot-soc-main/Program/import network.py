import network
import socket
import time
from machine import Pin, PWM

################################################ Konstatní proměnné
frequency = 5000
k = 20 #kolik proměnná
################################################ Proměnné
led = machine.Pin("LED", machine.Pin.OUT)

g = PWM(Pin(26)) 
b = PWM(Pin(20))
r = PWM(Pin(18))

r.freq(frequency)
g.freq(frequency)
b.freq(frequency)

## názvy proměnných pro hodnoty pwm
## vzor: hx
## h zn. hodnota
## x ozn. barevný kanál (r,g,b)
hr = 255
hg = 150
hb = 50

ssid = 'Mihulovi'
password = '11072006'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

html = """<!DOCTYPE html>
<html>
    <head> <title>Pico W</title> </head>
    <body> <h1>Pico W</h1>
        <p>%s</p>
    </body>
</html>
"""

max_wait = 10
################################################ Funkce
def zvysit(kanal,kolik): #kolik - zvetsit o v intervalu od 0 do 255
    global hr
    global hg
    global hb
    if kanal == 'r':
        hr = hr + kolik
        if hr >= 255:
            hr = 255
    if kanal == 'g':
        hg = hg + kolik
        if hg >= 255:
            hg = 255
    if kanal == 'b':
        hb = hb + kolik
        if hb >= 255:
            hb = 255

def snizit(kanal,kolik): #kolik - zmensit o v intervalu od 0 do 255
    global hr
    global hg
    global hb
    if kanal == 'r':
        hr = hr - kolik
        if hr <= 0:
            hr = 0
    if kanal == 'g':
        hg = hg - kolik
        if hg <= 0:
            hg = 0
    if kanal == 'b':
        hb = hb - kolik
        if hb <= 0:
            hb = 0

################################################ Kód + Inicializace (s definicí proměnných)
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)

################################################ "Naslouchání" - nekonečná smyčka kódu
while True:
    try:
        ## r,g,b piny pwm:
        r.duty_u16(hr*257)
        g.duty_u16(hg*257)
        b.duty_u16(hb*257)

        cl, addr = s.accept()
        print('client connected from', addr)
        request = cl.recv(1024)
        print(request)

        request = str(request)
        led_on = request.find('/light/on')
        led_off = request.find('/light/off')
        
        color_str = request[11:17]
        r_str = color_str[0:2]
        g_str = color_str[2:4]
        b_str = color_str[4:6]
        print(color_str)
        print("r=" + r_str)
        print("g=" + g_str)
        print("b=" + b_str)

        hr = int(r_str, 16)
        hg = int(g_str, 16)
        hb = int(b_str, 16)

        ## názvy proměnných:
        ## vzor: xy (rp,gm,...)
        ## x - barevný kanál
        ## y - zvýšení/znížení hodnoty                  y náleží <0;255>
        ##  p   - plus  - zvýšení hodnoty
        ##  m   - mínus - snížení hodnoty

        rp = request.find('/led_r/on')
        rm = request.find('/led_r/off')

        gp = request.find('/led_g/on')
        gm = request.find('/led_g/off')

        bp = request.find('/led_b/on')
        bm = request.find('/led_b/off')

        of = request.find('/col/off')

        #print( 'led on = ' + str(led_on))
        #print( 'led off = ' + str(led_off))

        if led_on == 6:
            print("led on")
            led.value(1)
            stateis = "LED - ON"

        if led_off == 6:
            print("led off")
            led.value(0)
            stateis = "LED - OFF"

        if rp == 6:
            zvysit('r',k)
            stateis = "R - p"
        if rm == 6:
            snizit('r',k)
            stateis = "R - m"

        if gp == 6:
            zvysit('g',k)
            stateis = "G - p"
        if gm == 6:
            snizit('g',k)
            stateis = "G - m"
        if bp == 6:
            zvysit('b',k)
            stateis = "B - p"
        if bm == 6:
            snizit('b',k)
            stateis = "B - m"
        if of == 6:
            snizit('r',255)
            snizit('g',255)
            snizit('b',255)
            stateis = "off"
        else:
            stateis = "barva"

        print("hr="+str(hr))
        print("hg="+str(hg))
        print("hb="+str(hb))
        print("  ")
        print("  ")

        response = html % stateis

        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

    except OSError as e:
        cl.close()
        s.close()
        print('connection closed')

