import machine
import utime

import config
from functioncycle import FunctionCycle
from utils import *
from touchcontroller import TouchController
from scheduler import Scheduler
from logging import logger
from mqtt_client import mqtt_client


# The signal to activate the relays is to connect to GND so logic is inverted.
# These help invert the logic in a logical way.
on = False
off = True

# Main switch: False = Closed = Lights off
main_lights = machine.Pin(25, machine.Pin.OPEN_DRAIN, value=off)
# Main lights mode: Relay resting: mode 1 (dimmed), relay activated: mode 2 (full power)
main_lights_mode = machine.Pin(26, machine.Pin.OPEN_DRAIN, value=off)
# Stove lights - False = Open = Lights off
stove_lights = machine.Pin(27, machine.Pin.OPEN_DRAIN, value=off)


def lights_off():
    print('Setting lights to off')
    main_lights.value(off)
    main_lights_mode.value(off)
    stove_lights.value(off)


def lights_dim():
    print('Setting lights to dim')
    main_lights.value(on)
    main_lights_mode.value(off)
    stove_lights.value(off)


def lights_full():
    print('Setting lights to full')
    main_lights.value(on)
    # Mode 2: full power
    main_lights_mode.value(on)
    stove_lights.value(on)


fcycle = FunctionCycle([lights_off, lights_dim, lights_full])
# Init at first entry
fcycle()


def publish_state(level):
    try:
        mqtt_client.publish(config.MQTT_GET_TOPIC, level)
    except Exception as e:
        logger.error('MQTT publish failed: {}'.format(e))


def touch_callback():
    fcycle()
    publish_state(str(fcycle.index))


tc = TouchController(
    pin=config.TOUCH_PIN,  # "G14"
    callback=touch_callback,
    # Config overrides
    avg_count=config.TOUCH_MEANCOUNT,
    samplerate=config.TOUCH_SAMPLERATE,
    threshold=config.TOUCH_THRESHOLD,
    debounce_ms=config.TOUCH_DEBOUNCE,
)


def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()
    logger.info('Received message from MQTT. topic: {}, msg: {}'.format(
        topic, msg
    ), stdout=True)
    if topic == config.MQTT_SET_TOPIC:
        index = int(msg)
        # Catch echos and redundant calls
        if fcycle.index == index:
            print('Skipping setting same index as already set')
            return
        fcycle(index)
    elif topic == config.MQTT_DEBUG_TOPIC:
        try:
            logger.connect()
        except:
            pass


def check_mqtt():
    mqtt_client.check_msg()


def connect_wifi_and_mqtt(force_mqtt=False):
    did_connect = wifi_connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    if did_connect or force_mqtt:
        utime.sleep_ms(500)
        # A new connection was established, do the same for MQTT
        logger.info('Connecting to MQTT...')
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        mqtt_client.subscribe(config.MQTT_SET_TOPIC)
        mqtt_client.subscribe(config.MQTT_DEBUG_TOPIC)
        logger.info('Connected to MQTT and subscribed.')


connect_wifi_and_mqtt(force_mqtt=True)
# Report current state
publish_state(str(fcycle.index))

scheduler = Scheduler(
    sleep_ms=tc.sample_sleep_ms,
    tasks=[
        (connect_wifi_and_mqtt, 1000),
        (check_mqtt, 1000),
        (tc.poll, tc.sample_sleep_ms)
    ]
)
scheduler.run()
