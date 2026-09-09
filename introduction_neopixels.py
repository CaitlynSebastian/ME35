import neopixel
import time
from machine import Pin
lights = neopixel.NeoPixel(Pin(15),2)
i=0

for i in range(5):
    lights[0]=(225,0,0)
    lights[1]=(0,225,0)
    lights.write()

    time.sleep(2)
    lights[0]=(20,0,20)
    lights[1]=(20,0,20)
    lights.write()

    time.sleep(2)
    lights[0]=(0,0,0)
    lights[1]=(0,0,0)
    lights.write()
    