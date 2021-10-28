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
pump = Pin(32, Pin.OUT, value=0)
light = Pin(33, Pin.OUT, value=0)

i2c = I2C(1, sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c) # 14 chars for a row

client = MQTTClient(client_id = "HSControllerSMA", server = "185.213.2.21", user = "S2mP9JgLQWjkp5D7mwIgNe6R9h3By7xfZHUWe1vVLF5YyyVKSrQuvKbuR2TgXelK") # self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}

def update_time():
    try:
        settime()
    except(OSError):
        pub_msg("log", "time_sync_error")
        pass
    time = localtime()
    global h
    h = time[3] + 3
    global m
    m = time[4]

def clear_screen():
    display.fill(0)
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

def light_control():
    pass

def watering_cycle():
    global L1_status
    global mode
    L1_status = L1.value() # check the water level in the bottom tank
    if L1_status != 0 and 22 > h > 9: # TODO: took hours of the dawn and sunset from the WEB and put here
        # put the start time into the DB
        mode = "watering" # update the mode value to "watering"
        pump.on() # turn on the water pump
        pub_msg("pump/state", 1)
    elif L1_status == 0:
        pub_msg("water_level/L1", "0") # send msg about the low water level
    # measure what time takes to finish the full cycle and
    pass

def system_check():
    global h
    global m
    L1_status = L1.value()
    L2_status = L2.value()
    pump_state = pump.value()
    light_state = light.value()
    if L1_status == 0 and pump_state == True:
        pump.off() # switch off the pump if no water in L1
    client.connect(clean_session=True)
    pub_msg("water_level/L1", L1_status)
    pub_msg("water_level/L2", L2_status)
    pub_msg("pump/state", pump_state)
    pub_msg("light/state", light_state)

def main():
    update_time()
    system_check()

if __name__ == '__main__':
    pub_msg("mode", mode)
    while True:
        main()
