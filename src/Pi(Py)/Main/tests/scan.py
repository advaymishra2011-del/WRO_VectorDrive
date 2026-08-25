import board
import adafruit_tca9548a

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)

for ch in range(8):
    bus = tca[ch]

    while not bus.try_lock():
        pass

    try:
        devices = bus.scan()

        # The TCA itself can appear through the proxy,
        # so ignore 0x70.
        devices = [hex(x) for x in devices if x != 0x70]

        print(f"Channel {ch}: {devices}")

    finally:
        bus.unlock()