import network


def wifi_connect():
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        return

    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('icanhasinternetz', '-')
    while not sta_if.isconnected():
        pass
    print('network config:', sta_if.ifconfig())