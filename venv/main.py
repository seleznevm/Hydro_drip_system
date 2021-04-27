import time, I2C, Pin
import gc
import ssd1306
from umqtt.simple import MQTTClient

i2c = I2C(-1, Pin(21), Pin(22))
display = ssd1306.SSD1306_I2C(128, 32, i2c)
display.text("Hello world!", 1, 1, 1)
display.show()

def connect_to_broker(server="5.196.95.208"):
    c = MQTTClient("esp32_682", server)
    c.connect()
    c.publish(b"SMA_hydro", b"Device is connected")
    c.disconnect()
    gc.collect()

def main():
    pass

if __name__ == '__main__':
    main()
