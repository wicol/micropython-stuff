from umqtt.robust import MQTTClient

import config

mqtt_client = MQTTClient(
    server=config.MQTT_SERVER,
    client_id=config.MQTT_CLIENT_ID,
    user=config.MQTT_USER,
    password=config.MQTT_PASSWORD,
)
mqtt_client.DEBUG = True
