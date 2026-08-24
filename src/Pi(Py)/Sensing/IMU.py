import time
import math
import board
import busio

from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR


# =========================================================
# BNO SETUP
# =========================================================

i2c = busio.I2C(
    board.SCL,
    board.SDA,
    frequency=100000
)

bno = BNO08X_I2C(i2c)

bno.enable_feature(
    BNO_REPORT_ROTATION_VECTOR,
    20000          # 50 Hz
)

bad_packets = 0


# =========================================================
# BNO REINITIALIZATION
# =========================================================

def reinitBNO():
    global bno

    print("Reinitializing BNO...")

    i2c = busio.I2C(
        board.SCL,
        board.SDA,
        frequency=100000
    )

    bno = BNO08X_I2C(i2c)

    bno.enable_feature(
        BNO_REPORT_ROTATION_VECTOR,
        20000
    )

    print("BNO reinitialized")


# =========================================================
# GET YAW
# =========================================================

def getRot():
    global bad_packets

    while True:

        try:
            i, j, k, real = bno.quaternion

            yaw = math.degrees(
                math.atan2(
                    2.0 * (real * k + i * j),
                    1.0 - 2.0 * (j * j + k * k)
                )
            )

            bad_packets = 0

            return yaw

        except (KeyError, IndexError, RuntimeError, OSError) as e:

            bad_packets += 1

            print("BNO packet error:", repr(e))

            if bad_packets >= 3:

                try:
                    reinitBNO()
                    bad_packets = 0

                except Exception as re:
                    print(
                        "BNO reinitialization failed:",
                        repr(re)
                    )

            time.sleep(0.02)

try:
    while True:
        # ax, ay, az = bno.acceleration
        # print("ACCEL:", ax, ay, az)

        # gx, gy, gz = bno.gyro
        # print("GYRO:", gx, gy, gz)

        # i, j, k, real = bno.quaternion
        # print("QUAT:", i, j, k, real)

        # mx, my, mz = bno.magnetic
        # print("MAG:", mx, my, mz)

        rot = getRot(bno)
        print(f"ROT: {rot:.2f} degrees")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")