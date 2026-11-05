import network
import espnow
import time
import neopixel
from machine import Pin

lights = neopixel.NeoPixel(Pin(15), 2)

sta = network.WLAN(network.WLAN.IF_STA)
sta.active(True)
sta.disconnect()

e = espnow.ESPNow()
e.active(True)

COLORS = {
    b'red':   (60, 0, 0),
    b'green': (0, 60, 0),
    b'blue':  (0, 0, 60),
}

def flash(color, duration=1):
    lights[0] = color
    lights.write()
    time.sleep(duration)
    lights[0] = (0, 0, 0)
    lights.write()

while True:
    mac, msg = e.recv(100)      # wait up to 100 ms for a message
    if mac is not None:
        print(msg)
        color = COLORS.get(bytes(msg))
        if color:
            flash(color)