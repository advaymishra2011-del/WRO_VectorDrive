import time
import math
import board
import busio

from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR


def create_bno():
    i2c = busio.I2C(
        board.SCL,
        board.SDA,
        frequency=100000
    )

    bno = BNO08X_I2C(i2c)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR, 20000)

    return bno


def getRot(bno):
    i, j, k, real = bno.quaternion

    yaw = math.degrees(math.atan2(
        2.0 * (real * k + i * j),
        1.0 - 2.0 * (j * j + k * k)
    ))

    return yaw


bno = create_bno()
last_yaw = None
bad_packets = 0

while True:
    try:
        yaw = getRot(bno)

        # Only accept a genuinely new-looking value.
        if last_yaw is None:
            last_yaw = yaw

        print(f"Yaw: {yaw:.2f}°")
        last_yaw = yaw
        bad_packets = 0

    except (KeyError, IndexError, RuntimeError, OSError) as e:
        bad_packets += 1
        print("BNO error:", repr(e))

        if bad_packets >= 3:
            print("Reinitializing BNO...")
            time.sleep(0.2)

            try:
                bno = create_bno()
                bad_packets = 0
                print("BNO reinitialized")
            except Exception as re:
                print("Reinitialization failed:", repr(re))

        time.sleep(0.02)