import network


def wifi_connect(ssid, password):
    sta_if = network.WLAN(network.STA_IF)
    print('Connecting to network...')
    sta_if.active(True)
    sta_if.connect(ssid, password)


def wifi_connected():
    sta_if = network.WLAN(network.STA_IF)
    return sta_if.isconnected()


def ifconfig():
    sta_if = network.WLAN(network.STA_IF)
    print('Network config:', sta_if.ifconfig())


def write_config(path, config):
    """
    Write config directives to path. Crude implementation - should work for basic types.
    :param path: path to write to
    :param config: config module or object with config attributes
    """
    s = ''
    for name in sorted(dir(config)):
        # Only save attributes that start with an uppercase letter -
        # those should be our config directives
        if not name[0].isupper():
            continue
        v = getattr(config, name)
        s += '{} = {}\n'.format(name, repr(v))

    open(path, 'w').write(s)
    print('Saved config to {}'.format(path))
