import machine

MCP41_CMD_SET_RESISTANCE = bytearray([0b00010001])
MCP41_CMD_SHUT_DOWN = bytearray([0b00100001])


class Regulator:
    def __init__(self):
        # Note: when using 255 the pot seems to get stuck :|
        self.levels = [254, 50, 0]
        self.current_level = None
        self.generator = self.make_generator()
        self.spi = None
        self.spi = machine.SPI(
            baudrate=9600,
            # SCK idle state is low (irrelevant?)
            polarity=0,
            # Write on first edge? Might be 1 depending on how this is implemented
            phase=0,
            sck=machine.Pin(18),  # SCK/Clock/Sync
            mosi=machine.Pin(23),  # (MO)SI - Data in (to MCP)
            miso=machine.Pin(19)  # (MI)SO - Data out (from MCP) (Unused)
        )
        # SPI CS / Chip Select
        self.sspin = machine.Pin(22, machine.Pin.OUT)
        # Set chip select base level
        self.sspin.value(True)
        # Set initial value (off)
        self.set_level(0)

    def set_resistance(self, value):
        self.sspin.value(False)
        self.spi.write(MCP41_CMD_SET_RESISTANCE)
        self.spi.write(bytearray([value]))
        self.sspin.value(True)

    def make_generator(self):
        while True:
            for level in self.levels:
                yield level

    def next_level(self):
        self.set_level(next(self.generator))

    def set_level(self, level):
        print('Setting level: {}'.format(level))
        self.set_resistance(level)
        self.current_level = level
