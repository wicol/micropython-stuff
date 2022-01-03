WIFI_SSID = ""
WIFI_PASSWORD = ""
MQTT_SERVER = "192.168.0.90000000"
MQTT_CLIENT_ID = "fan-controller"
MQTT_USER = ""
MQTT_PASSWORD = ""

MQTT_TOPIC_BASE = "homeassistant/fan/cinemafans"
MQTT_TOPIC_AVAILABILITY = MQTT_TOPIC_BASE + "/availability"
MQTT_TOPIC_COMMAND = MQTT_TOPIC_BASE + "/set"
MQTT_TOPIC_STATE = MQTT_TOPIC_BASE + "/state"
MQTT_TOPIC_PERCENTAGE_COMMAND = MQTT_TOPIC_BASE + "/speed/set"
MQTT_TOPIC_PERCENTAGE_STATE = MQTT_TOPIC_BASE + "/speed/state"
MQTT_TOPIC_REPORT = MQTT_TOPIC_BASE + "/report"


MQTT_AUTODISCOVERY_TOPIC = MQTT_TOPIC_BASE + "/config"
MQTT_AUTODISCOVERY_PAYLOAD = {
    "name": "Cinema fans",
    "object_id": "cinema_fans",
    "availability_topic": MQTT_TOPIC_AVAILABILITY,
    "command_topic": MQTT_TOPIC_COMMAND,
    "state_topic": MQTT_TOPIC_STATE,
    "percentage_command_topic": MQTT_TOPIC_PERCENTAGE_COMMAND,
    "percentage_state_topic": MQTT_TOPIC_PERCENTAGE_STATE,
    "retain": True,
}

PWM_PIN = 5  # GPIO 5
POWER_PIN = 25  # GPIO 25
POWER_PIN_INVERTED = False
