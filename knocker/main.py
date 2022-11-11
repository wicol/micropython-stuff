import json
import machine
import network
import utime

import config
from umqtt.robust import MQTTClient


class KnockSequenceHandler:
    def __init__(self, sequence, precision=110):
        self.sequence = None
        self.sequence_length = None
        self.precision = precision
        self.sequence_scaled = None
        self.first_knock_ticks = None
        self.last_knock_ticks = None
        self.cursor = None
        self.set_sequence(sequence)

    def set_sequence(self, sequence):
        self.sequence = sequence
        self.sequence_length = len(sequence)

    def reset(self):
        self.sequence_scaled = None
        self.first_knock_ticks = None
        self.last_knock_ticks = None
        self.cursor = None

    def is_knocking(self):
        return self.cursor is not None

    def knock(self, ticks):
        if not ticks:
            return self.timeout()

        # First knock
        if self.cursor is None:
            self.first_knock_ticks = self.last_knock_ticks = ticks
            self.cursor = 0
            print(self.sequence)
            print(self.cursor)
            return

        self.cursor += 1
        if self.cursor == 1:
            # Second knock - now we can scale the sequence
            # Except if it's too close to the first one - then fail
            if utime.ticks_diff(ticks, self.last_knock_ticks) < 100:
                self.reset()
                return False
            self.scale_sequence(ticks)
            print(self.sequence_scaled)

        if not self.knock_matches_sequence(ticks):
            # Knock doesn't match pattern
            self.reset()
            return False

        self.last_knock_ticks = ticks
        if self.cursor == self.sequence_length - 1:
            # Full sequence matched!
            self.reset()
            return True

    def knock_matches_sequence(self, ticks):
        target = self.sequence_scaled[self.cursor]
        offset_from_first = utime.ticks_diff(ticks, self.first_knock_ticks)
        result = target - self.precision < offset_from_first < target + self.precision
        print(self.cursor, target, offset_from_first, offset_from_first - target, result)
        return result

    def scale_sequence(self, ticks):
        offset_from_first = utime.ticks_diff(ticks, self.first_knock_ticks)
        offset_in_sequence = self.sequence[1]
        ratio = offset_from_first / offset_in_sequence
        self.sequence_scaled = [t * ratio for t in self.sequence]

    def timeout(self):
        if self.is_knocking() and utime.ticks_diff(utime.ticks_ms(), self.last_knock_ticks) > 2000:
            print("Timeout")
            self.reset()


class SensorHandler:
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.latest_event = None
        self.valid_event = None
        self.pin.irq(self.set_ticks)

    def set_ticks(self, pin):
        ticks = utime.ticks_ms()
        # debounce

        diff = utime.ticks_diff(ticks, self.latest_event)

        if diff > 100:
            print("last: %s, ticks: %s, diff: %s - valid" % (self.latest_event, ticks, diff))
            self.valid_event = ticks
        else:
            print("last: %s, ticks: %s, diff: %s" % (self.latest_event, ticks, diff))

        self.latest_event = ticks

    def get_ticks(self):
        if self.valid_event:
            ticks = self.valid_event
            self.valid_event = None
            return ticks


class Knocker:
    def __init__(self):
        self.sequence_handler = KnockSequenceHandler(config.KNOCKER_SEQUENCE)
        self.sensor_handler = SensorHandler(config.SENSOR_PIN)
        self.mqtt_client = MQTTClient(
            server=config.MQTT_SERVER,
            client_id=config.MQTT_CLIENT_ID,
            user=config.MQTT_USER,
            password=config.MQTT_PASSWORD,
            keepalive=config.MQTT_KEEPALIVE_INTERVAL + 10,
        )
        self.mqtt_client.DEBUG = True
        self.last_mqtt_packet = None
        self.last_rssi_check = None
        self.wlan = network.WLAN(network.STA_IF)
        self.calibration_mode = False

    def success(self):
        self.publish()

    def failure(self):
        print("Fail!")

    def publish(self):
        print("Publishing")
        try:
            self.mqtt_client.publish(config.MQTT_TOPIC, "on")
            self.last_mqtt_packet = utime.ticks_ms()
        except Exception as e:
            print("MQTT publish failed: {}".format(e))

    def publish_calibration(self):
        print("Publishing calibration knock")
        try:
            self.mqtt_client.publish(config.MQTT_TOPIC_CALIBRATE, str(utime.ticks_ms()))
        except Exception as e:
            print("MQTT publish failed: {}".format(e))

    def get_config(self):
        print("Getting configuration from MQTT...")

        def callback(topic, msg):
            topic = topic.decode()
            msg = msg.decode()
            if topic == config.MQTT_TOPIC_CALIBRATE and msg == "true":
                print("Found calibration configuration: ", msg)
                self.calibration_mode = True
            elif topic == config.MQTT_TOPIC_SEQUENCE:
                print("Found sequence configuration: ", msg)
                self.sequence_handler.set_sequence(json.loads(msg))

        self.mqtt_client.set_callback(callback)
        self.mqtt_client.subscribe(config.MQTT_TOPIC_CALIBRATE)
        self.mqtt_client.subscribe(config.MQTT_TOPIC_SEQUENCE)
        utime.sleep(1)
        self.mqtt_client.check_msg()
        utime.sleep(5)
        self.mqtt_client.unsubscribe(config.MQTT_TOPIC_CALIBRATE)
        self.mqtt_client.unsubscribe(config.MQTT_TOPIC_SEQUENCE)

    def run(self):
        print("Connecting to MQTT...")
        self.mqtt_client.reconnect()
        self.last_mqtt_packet = utime.ticks_ms()
        print("MQTT connected")

        self.get_config()
        utime.sleep(1)
        print("Calibration mode:", self.calibration_mode)

        print("Sequence is:", self.sequence_handler.sequence)

        print("Waiting for knocks...")
        while True:
            utime.sleep_ms(20)
            now = utime.ticks_ms()
            if not self.sequence_handler.is_knocking():
                if utime.ticks_diff(now, self.last_mqtt_packet) > config.MQTT_KEEPALIVE_INTERVAL * 1000:
                    print("MQTT Ping")
                    self.mqtt_client.ping()
                    self.last_mqtt_packet = now
                if utime.ticks_diff(now, self.last_rssi_check) > 10000:
                    print("Wifi signal strength: %s" % self.wlan.status("rssi"))
                    self.last_rssi_check = now

            ticks = self.sensor_handler.get_ticks()

            if self.calibration_mode and ticks:
                self.publish_calibration()
                continue

            result = self.sequence_handler.knock(ticks)
            if result is None:
                continue
            elif result is True:
                self.success()
            elif result is False:
                self.failure()
            utime.sleep(1)
            print("Starting over")


# 1,2,3,4,5,7,11,13
# 0,1,2,3,4,6,10,12
# 0,100,200,300,400,600,1000,1200
# 100,300
# 00001111101000101000
