import json
import machine
import time
import gc
from umqtt.simple import MQTTClient

import config


class FanController:
    def __init__(self):
        self.t_start = time.ticks_ms()

    def setup_pins(self):
        self.pwm = machine.PWM(machine.Pin(config.PWM_PIN))
        self.pwm.freq(2000)
        self.power_pin = machine.Pin(
            config.POWER_PIN, machine.Pin.OUT, value=config.POWER_PIN_INVERTED
        )

    def setup_mqtt(self):
        self.t_mqtt_start = time.ticks_ms()
        self.mqtt_client = MQTTClient(
            server=config.MQTT_SERVER,
            client_id=config.MQTT_CLIENT_ID,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD,
            keepalive=20,
        )
        self.mqtt_client.DEBUG = True
        self.mqtt_client.set_callback(self.mqtt_callback)
        self.mqtt_client.set_last_will(
            config.MQTT_TOPIC_AVAILABILITY, "offline", retain=True
        )
        self.mqtt_client.connect()

        self.mqtt_client.subscribe(config.MQTT_TOPIC_COMMAND)
        self.mqtt_client.subscribe(config.MQTT_TOPIC_PERCENTAGE_COMMAND)

        # Get and apply retained values before publishing state
        self.mqtt_client.check_msg()

        self.mqtt_client.publish(config.MQTT_TOPIC_AVAILABILITY, "online", retain=True)
        self.mqtt_client.publish(
            config.MQTT_TOPIC_STATE, "ON" if self.get_power() else "OFF", retain=True
        )
        self.mqtt_client.publish(
            config.MQTT_TOPIC_PERCENTAGE_STATE, str(self.get_speed()), retain=True
        )
        self.mqtt_client.publish(
            config.MQTT_AUTODISCOVERY_TOPIC,
            json.dumps(config.MQTT_AUTODISCOVERY_PAYLOAD),
            retain=True,
        )

    def mqtt_callback(self, topic, msg):
        topic = topic.decode("utf-8")
        msg = msg.decode("utf-8")
        print(f"Received topic:msg: {topic}:{msg}")
        # Handle state topics because we fetch from that initially to resume session
        if topic in [config.MQTT_TOPIC_STATE, config.MQTT_TOPIC_COMMAND] and msg in (
            "ON",
            "OFF",
        ):
            self.set_power(msg == "ON")
            if topic == config.MQTT_TOPIC_COMMAND:
                self.mqtt_client.publish(config.MQTT_TOPIC_STATE, msg, retain=True)
        elif topic in [
            config.MQTT_TOPIC_PERCENTAGE_STATE,
            config.MQTT_TOPIC_PERCENTAGE_COMMAND,
        ]:
            self.set_speed(int(msg))
            if topic == config.MQTT_TOPIC_PERCENTAGE_COMMAND:
                self.mqtt_client.publish(
                    config.MQTT_TOPIC_PERCENTAGE_STATE, msg, retain=True
                )
        else:
            print(f"Unhandled topic:msg: {topic}:{msg}")

    def run(self):
        try:
            t_last_print = t_last_ping = t_last_report = 0
            while True:
                self.mqtt_client.check_msg()
                ticks = time.ticks_ms()
                if time.ticks_diff(ticks, t_last_print) > 1000:
                    print("Running...")
                    t_last_print = ticks
                if time.ticks_diff(ticks, t_last_ping) > 10000:
                    print("MQTT ping")
                    self.mqtt_client.ping()
                    t_last_ping = ticks
                if time.ticks_diff(ticks, t_last_report) > 60000:
                    print("MQTT report")
                    self.mqtt_client.publish(
                        config.MQTT_TOPIC_REPORT, self.get_report(as_string=True)
                    )
                    t_last_report = ticks
                time.sleep_ms(100)
        finally:
            # sock.close sends last will - disconnect doesn't
            self.mqtt_client.sock.close()

    def get_speed(self):
        # Duty -> percent
        return int(self.pwm.duty() / 1023 * 100)

    def set_speed(self, pct: int):
        # Percent -> decimal
        dec = pct / 100
        # Decimal -> duty
        duty = int(1023 * dec)
        print(f"Setting speed: {pct}% / {duty}")
        self.pwm.duty(duty)

    def get_power(self):
        return self.power_pin.value() != config.POWER_PIN_INVERTED

    def set_power(self, val: bool):
        val = val != config.POWER_PIN_INVERTED
        print(f"Setting power: {val}")
        self.power_pin.value(val)

    def get_report(self, as_string=False):
        mem_before = gc.mem_free()
        gc.collect()
        mem_after = gc.mem_free()
        report = {
            "power": self.get_power(),
            "speed": self.get_speed(),
            "mem_before": mem_before,
            "mem_after": mem_after,
            "uptime": int(time.ticks_diff(time.ticks_ms(), self.t_start) / 1000),
            "mqtt_uptime": int(
                time.ticks_diff(time.ticks_ms(), self.t_mqtt_start) / 1000
            ),
        }
        if not as_string:
            return report

        return "\n".join([f"{k}: {v}" for k, v in report.items()])
