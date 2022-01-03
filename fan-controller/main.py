import machine
import time
from fancontroller import FanController
from wifi import setup_wifi

try:
    while not setup_wifi():
        time.sleep(10)
    print("Setting up FanController...")
    fc = FanController()
    fc.setup_pins()

    # Outer main loop - init/re-init
    while True:
        print("Initializing MQTT...")
        fc.setup_mqtt()
        try:
            fc.run()
        except OSError as e:
            print(f"{e} :(")
            time.sleep_ms(5000)

except KeyboardInterrupt:
    print("Quitting")
except Exception:
    time.sleep(5)
    machine.reset()
