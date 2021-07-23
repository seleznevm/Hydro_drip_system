#123
import time
from machine import I2C, Pin
import gc
import ssd1306
from umqtt.simple import MQTTClient
from ntptime import settime
global mode
mode = "initialization"
tank_L1 = Pin(34, Pin.IN)
tank_L1_status = tank_L1.value()
tank_L2 = Pin(35, Pin.IN)
tank_L2_status = tank_L2.value()
pump = Pin(32, Pin.OUT, value=0)
light = Pin(33, Pin.OUT, value=0)

i2c = I2C(1, sda=Pin(21), scl=Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c) # 14 chars for a row

client = MQTTClient("esp32_Mike", "192.168.1.246", port = 1883) # self, client_id, server, port=0, user=None, password=None, keepalive=0, ssl=False, ssl_params={}

def update_time():
    try:
        settime()
    except(OSError):
        pub_msg("SMA_status/log", "time_sync_error")
        pass
    Time = time.localtime()
    global h
    h = Time[3] + 3
    global m
    m = Time[4]

def clear_screen():
    display.fill(0)
    display.show()

def display_main():
    clear_screen()
    display.text("mode: "+str(mode), 1,1)
    display.text("Pump: "+str(pump.value()),1,10)
    display.text("L1 level: " + str(tank_L1_status), 1, 20)
    display.show()

def pub_msg(topic, msg):
    client = MQTTClient("esp32_Mike", "mqtt.flespi.io")
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
    global tank_L1_status
    tank_L1_status = tank_L1.value() # check the water level in the bottom tank
    if tank_L1_status != 0 and 22 > h > 9:
        # put the start time into the DB
        global mode
        mode = "watering" # update the mode value to "watering"
        pump.on() # turn on the water pump
        pub_msg("SMA_pump", 1)
    elif tank_L1_status == 0:
        pub_msg("SMA_status/L1_level", "0") # send msg about the low water level
    # measure what time takes to finish the full cycle and
    pass

def system_check():
    tank_L1_status = tank_L1.value()
    if tank_L1_status == 0: pub_msg("SMA_status/L1_level", "0")
    else: pub_msg("SMA_status/L1_level", "1")
    pub_msg("SMA_status/system_time", str(h)+":"+str(m))

def main():
    update_time()
    system_check()
    display_main()
    if mode != "watering" or "draining":
        watering_cycle() # run watering cycle
    tank_L1_status = tank_L1.value() #check the bottom tank level
    if tank_L1_status == 0:  # if water level sensor in the bottom tank = 0 then turn off the pump
        pump.off() 

if __name__ == '__main__':
    pub_msg("SMA_status", mode)
    while True:
        main()
