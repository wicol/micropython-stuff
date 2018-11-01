def wifi_connect(ssid, password):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        return False

    print('Connecting to network...')
    sta_if.active(True)
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
        pass
    print('Network config:', sta_if.ifconfig())
    return True


def ifconfig():
    import network
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
