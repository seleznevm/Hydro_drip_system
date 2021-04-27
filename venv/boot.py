import network
import gc
APP_NAME = 'SMA'
APP_PWD = 'ipc2320207'

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(APP_NAME, APP_PWD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

do_connect()
gc.collect()