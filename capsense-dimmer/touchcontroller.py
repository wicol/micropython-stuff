import machine
import utime

from logging import logger


class TouchController:
    def __init__(self, pin, callback, *args, **kwargs):
        self.pin = machine.Pin(pin)
        self.touchpin = machine.TouchPad(self.pin)
        self.callback = callback
        self.avg_count = 15
        self.samplerate = 120
        self.threshold = 0.95
        self.debounce_ms = 300
        self.sample_sleep_ms = int(1000/self.samplerate)
        self.readings = []
        self.configure(kwargs)
        self.callback_triggered_last = utime.ticks_ms()
        # Initial calibration
        for i in range(self.avg_count):
            utime.sleep_ms(self.sample_sleep_ms)
            self.readings.append(self.touchpin.read())

    def configure(self, config):
        # Override defaults
        for k, v in config.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.sample_sleep_ms = int(1000 / self.samplerate)

    def get_current_mean(self):
        return int(sum(self.readings) / len(self.readings))

    def poll(self):
        value = self.touchpin.read()
        weighted_value = sum(self.readings[-2:] + [value]) / 3
        mean = self.get_current_mean()
        thresh = mean * self.threshold
        ratio = weighted_value / mean
        #logger.debug(
        #    '[{}] Mean: {:04.0f}, Threshold: {:04.0f}, This: {:04.0f}, This weighted: {:04.0f} / {:.0%}'
        #    .format(utime.ticks_ms(), mean, thresh, value, weighted_value, ratio)
        #)
        # logger.debug('{} {} {}'.format(mean, weighted_value, int(ratio*100)))

        if weighted_value < thresh:
            now = utime.ticks_ms()
            if (utime.ticks_diff(now, self.callback_triggered_last)
                    < self.debounce_ms):
                logger.info('Debounced')
                # Make reading affect mean less - this allows for slow recalibration
                #value += (thresh - value)*0.9
            else:
                self.callback()
                self.callback_triggered_last = now
        self.readings.pop(0)
        self.readings.append(weighted_value)

    def run(self):
        while True:
            self.poll()
