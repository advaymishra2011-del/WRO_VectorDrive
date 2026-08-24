import time
import board
import adafruit_tca9548a
import adafruit_vl53l0x

# Main Pi I2C bus
i2c = board.I2C()

# TCA9548A
tca = adafruit_tca9548a.TCA9548A(i2c)

# VL53L0X sensors
tofs = {
    "front": adafruit_vl53l0x.VL53L0X(tca[0]),
    "left": adafruit_vl53l0x.VL53L0X(tca[1]),
    "right": adafruit_vl53l0x.VL53L0X(tca[2]),
    "rear_left": adafruit_vl53l0x.VL53L0X(tca[3]),
    "rear_right": adafruit_vl53l0x.VL53L0X(tca[4]),
}


def getDistances(tofs):
    distances = {}

    for name, sensor in tofs.items():
        try:
            distances[name] = sensor.range

        except (OSError, RuntimeError) as e:
            print(f"{name} ERROR: {repr(e)}")
            distances[name] = None

    return distances


try:
    while True:
        distances = getDistances(tofs)
        print("DISTANCES:", distances)

        time.sleep(0.05)  # 20 Hz

except KeyboardInterrupt:
    print("Exiting...")