import board
import adafruit_tcs34725
import time

i2c = board.I2C()

tcs = adafruit_tcs34725.TCS34725(i2c)

#Calibration
#tcs.gain = 
#tcs.integration_time = 

try:
    while True:

        print("RGB:", tcs.color_rgb_bytes)
        print("RAW:", tcs.color_raw)
        print("Temperature:", tcs.color_temperature)
        print("Lux:", tcs.lux)

        print()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")

def getColor():
    rgb = tcs.color_rgb_bytes
    return rgb