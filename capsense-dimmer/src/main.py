from src.regulator import Regulator
from src.touchcontroller import TouchController

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
# SCK/Sync: pin 18
# MOSI: pin 23
# MISO: pin 19
#
# CS/Sync: pin 0
