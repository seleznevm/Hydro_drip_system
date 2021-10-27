from time import localtime, sleep_ms
from machine import I2C, Pin
import gc
import ssd1306
from umqtt.simple2 import MQTTClient
from ntptime import settime

mode = "initialization"
L1 = Pin(34, Pin.IN)
L1_status = L1.value()
L2 = Pin(35, Pin.IN)
L2_status = L2.value()
pump = Pin(32, Pin.OUT, value=1)
light = Pin(33, Pin.OUT, value=1)

i2c = I2C(1, sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c) # 14 chars for a row

client = MQTTClient(client_id = "HSControllerSMA", server = "185.213.2.21", user = "jRveM9BFtx0YKH2zPy4vg07mBVkCMFtTmPWWMnr5KhTjOJIs5DN9rJlSuti7YCO8") # self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}

def update_time():
    try:
        settime()
    except(OSError):
        pub_msg("SMA_status/log", "time_sync_error")
        pass
    time = localtime()
    global h
    h = time[3] + 3
    global m
    m = time[4]

def clear_screen():
    display.fill(0)
    display.show()

def display_main():
    clear_screen()
    display.text("mode: "+str(mode), 1,1)
    display.text("Pump: "+str(pump.value()),1,10)
    display.text("L1 level: " + str(L1_status), 1, 20)
    display.show()

def pub_msg(topic, msg):
    try:
        client.connect()
        client.publish(str(topic), str(msg))
        client.disconnect()
    except:
        clear_screen()
        display.text("MQTT connection", 1, 10)
        display.text("error", 5, 20)
        display.show()
        pass
    gc.collect()

def light_control():
    pass

def watering_cycle():
    global L1_status
    L1_status = L1.value() # check the water level in the bottom tank
    if L1_status != 0 and 22 > h > 9:
        # put the start time into the DB
        global mode
        mode = "watering" # update the mode value to "watering"
        pump.on() # turn on the water pump
        pub_msg("SMA_pump", 1)
    elif L1_status == 0:
        pub_msg("SMA_status/L1_level", "0") # send msg about the low water level
    # measure what time takes to finish the full cycle and
    pass

def main():
    global mode
    update_time()
    display_main()

if __name__ == '__main__':
    pub_msg("SMA_status", mode)
    while True:
        main()
