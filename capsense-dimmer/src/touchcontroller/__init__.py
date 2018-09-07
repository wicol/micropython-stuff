import machine
import utime


class TouchController:
    def __init__(self, pin, callback, *args, **kwargs):
        self.pin = machine.Pin(pin)
        self.touchpin = machine.TouchPad(self.pin)
        self.callback = callback
        self.avg_count = 20
        self.samplerate = 100
        self.threshold = 0.95
        self.debounce_ms = 220
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

    def read(self):
        self.readings.pop(0)
        self.readings.append(self.touchpin.read())

    def get_current_mean(self):
        return int(sum(self.readings) / len(self.readings))

    def run(self):
        while True:
            utime.sleep_ms(self.sample_sleep_ms)
            self.read()
            mean = self.get_current_mean()
            thresh = mean * self.threshold
            latest = self.readings[-1]
            print(
                '[{}] Mean: {:04.0f}, Threshold: {:04.0f}, This: {:04.0f} / {:.0%}'
                .format(utime.ticks_ms(), mean, thresh, latest, latest/mean)
            )
            if latest < thresh:
                now = utime.ticks_ms()
                if utime.ticks_diff(
                        now, self.callback_triggered_last) < self.debounce_ms:
                    print('Debounced')
                    continue
                self.callback()
                self.callback_triggered_last = now
