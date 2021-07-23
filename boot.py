import network
from machine import I2C, Pin
import gc
import ssd1306
APP_NAME = 'MiKate2'
APP_PWD = 'yaslujukate'
i2c = I2C(1, sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

def clear_screen():
    display.fill(0)
    display.show()

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        display.text("connecting...",1,1)
        display.show()
        print('connecting to network...')
        wlan.connect(APP_NAME, APP_PWD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    IP_number = wlan.ifconfig()
    clear_screen()
    display.text("connection done", 1,1)
    display.show()
    display.text(str(IP_number), 1, 10)
    display.show()

clear_screen()
do_connect()
gc.collect()