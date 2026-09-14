import network
wlan = network.WLAN()
mac = wlan.config("mac")
print(mac)

import ubinascii
mac_readable = ubinascii.hexlify(mac,":").decode()
print(mac_readable)

#b' P\r*6\xf4'
#20:50:0d:2a:36:f4

#importing the libraries
import network
import urequests
import time



#setting up SSID and password 
 
SSID = "tufts_eecs" #use tufts_eecs
PASSWORD = "foundedin1883" #foundedin1883


#function definition 
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("Connected! IP address:", wlan.ifconfig()[0])
    return wlan
 
 #function call
connect_wifi()
 
 #ON REPL you can type wlan.isconnected() hit ENTER. it will return True

ISS_URL = "https://v6.exchangerate-api.com/v6/9aa8bed78631c7b7e26a1874/latest/USD"\

response = urequests.get(ISS_URL)
data = response.json()
response.close()

print(data)
