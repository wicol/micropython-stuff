from regulator import Regulator
from touchcontroller import TouchController
import config
from umqtt.simple import MQTTClient

r = Regulator()
tc = TouchController(
    pin=4,  # "G4"
    callback=r.next_level,
    # Config overrides
    avg_count=15,
    samplerate=150,
    threshold=0.95,
    debounce_ms=230,
)
tc.run()

# SPI
# SCK/Sync: GPIO 18
# MOSI: GPIO 23
# MISO: GPIO 19
#
# CS/Sync: GPIO 22


mqtt_client = MQTTClient({
    'client_id': config.MQTT_CLIENT_ID,
    'server': config.MQTT_SERVER,
    'user': config.MQTT_USER,
    'password': config.MQTT_PASSWORD,
})


def publish_level(level):
    try:
        mqtt_client.publish(config.MQTT_TOPIC, level)
        self.mqtt_client.disconnect()
    except Exception as e:
        print('MQTT publish failed: {}'.format(e))


def touch_callback():
    level = r.next_level()
    publish_level(level)


def mqtt_callback(topic, msg):
    print('Received message from MQTT. topic: {}, msg: {}'.format(
        topic, msg
    ))
    r.set_level(int(msg))


def connect_wifi_and_mqtt():
    res = wifi_connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    if res:
        # A new connection was established, do the same for MQTT
        mqtt_client.connect()
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.subscribe(config.MQTT_TOPIC)

Scheduler(
    sleep_ms=10,
    tasks=[
        (connect_wifi_and_mqtt, 1000),
        (mqtt_client.check_msg, 1000),
        (tc.poll, 10)
    ]
)
