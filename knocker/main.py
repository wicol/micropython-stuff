import machine
import utime


class Knocker:
    def __init__(self, sequence, precision=100):
        self.sequence = sequence
        self.sequence_length = len(sequence)
        self.precision = precision
        self.sequence_scaled = None
        self.first_knock_ticks = None
        self.last_knock_ticks = None
        self.cursor = None

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
            print('Timeout')
            self.reset()


class SensorHandler:
    def __init__(self, pin):
        self.pin = machine.Pin(pin, machine.Pin.IN)
        self.ticks = None
        self.new_ticks = False
        self.pin.irq(self.set_ticks)

    def set_ticks(self, pin):
        ticks = utime.ticks_ms()
        # dedupe
        if utime.ticks_diff(ticks, self.ticks) > 70:
            self.ticks = ticks
            self.new_ticks = True

    def get_ticks(self):
        if self.new_ticks:
            self.new_ticks = False
            return self.ticks


def success():
    print('Success!')


def failure():
    print('Fail!')


def main():
    sequence = [0, 1, 2, 4]
    knocker = Knocker(sequence)
    sensorhandler = SensorHandler(5)
    #sensorhandler.run()

    while True:
        utime.sleep_ms(20)
        ticks = sensorhandler.get_ticks()
        result = knocker.knock(ticks)
        if result is None:
            continue
        elif result is True:
            success()
        elif result is False:
            failure()
        utime.sleep(1)
        print("Starting over")

