import board
import busio
import time

from adafruit_bno08x.i2c import BNO08X_I2C

from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR
)

i2c = busio.I2C(
    board.SCL,
    board.SDA,
    frequency=400000
)

bno = BNO08X_I2C(i2c)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

#CALIBRATION
#bno.begin_calibration()
#bno.calibration_status
#bno.save_calibration_data()

try:
    while True:
        ax, ay, az = bno.acceleration
        print("ACCEL: ",ax, ay, az)

        gx, gy, gz = bno.gyro
        print("GYRO: ",gx, gy, gz)

        i, j, k, real = bno.quaternion
        print("QUAT: ",i, j, k, real)

        mx, my, mz = bno.magnetic
        print("MAG: ",mx, my, mz)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

def getRot(bno085):
    gx, gy, gz = bno085.gyro
    return gz

def wait(deg, bno085):
    while gz<=deg:
        gx, gy, gz = bno085.gyro
        time.sleep(0.005)
    return