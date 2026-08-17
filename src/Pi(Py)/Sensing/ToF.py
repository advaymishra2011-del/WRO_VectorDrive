import board
import adafruit_tca9548a
import adafruit_vl53l0x

# Main Pi I²C bus
i2c = board.I2C()

# TCA9548A multiplexer
tca = adafruit_tca9548a.TCA9548A(i2c)

# VL53L0X sensors
tofs = {
    "front": adafruit_vl53l0x.VL53L0X(tca[0]),
    "left": adafruit_vl53l0x.VL53L0X(tca[1]),
    "right": adafruit_vl53l0x.VL53L0X(tca[2]),
    "rear_left": adafruit_vl53l0x.VL53L0X(tca[3]),
    "rear_right": adafruit_vl53l0x.VL53L0X(tca[4])
}

distances = {
    name: sensor.range
    for name, sensor in tofs.items()
}

try:
    while True:
        print("DISTANCES: ", distances)
except KeyboardInterrupt:
    print("Exiting...")