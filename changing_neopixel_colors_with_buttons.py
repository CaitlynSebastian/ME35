import neopixel
import time
from machine import Pin
from time import ticks_ms, ticks_diff
lights = neopixel.NeoPixel(Pin(15),2)

btn = Pin(34, Pin.IN, Pin.PULL_UP) 
DEBOUNCE_MS = 200
last_press = 0


def button_handler(pin):
    global last_press, led
    now = ticks_ms()
    if ticks_diff(now, last_press) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press = now
            if (led):
                lights[0]=(20,0,20)
                lights[1]=(20,0,20)
                
                print("Button pressed!")
            else:
                lights[0]=(0,20,0)
                lights[1]=(0,20,0)
            lights.write()

btn.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)