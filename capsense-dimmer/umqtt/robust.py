import utime
from . import simple


class MQTTClient(simple.MQTTClient):

    DELAY = 0
    DEBUG = False

    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self, max_retries=0):
        # -1 to try at least once
        i = -1
        while i < max_retries:
            try:
                return super().connect(False)
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)

    def publish(self, topic, msg, retain=False, qos=0, max_retries=1):
        # -1 to try at least once
        i = -1
        while i < max_retries:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log(False, e)
                i += 1
            self.reconnect()

    def wait_msg(self, max_retries=1):
        # -1 to try at least once
        i = -1
        while i < max_retries:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()
