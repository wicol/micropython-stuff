import network
import utime

import config


def setup_wifi():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        print('Already connected')
        print('network config:', sta_if.ifconfig())
        return True
    
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        wait_start = utime.ticks_ms()
        while True:
            connected = sta_if.isconnected()
            utime.sleep_ms(500)
            if connected or utime.ticks_diff(utime.ticks_ms(), wait_start) > 7000:
                break
        if connected:
            print('network config:', sta_if.ifconfig())
            return True
        print('Failed connecting to', config.WIFI_SSID)
