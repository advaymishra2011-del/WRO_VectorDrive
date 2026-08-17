import board
import adafruit_tcs34725

i2c = board.I2C()

tcs = adafruit_tcs34725.TCS34725(i2c)

#Calibration
#tcs.gain = 
#tcs.integration_time = 

while True:

    print("RGB:", tcs.color_rgb_bytes)
    print("RAW:", tcs.color_raw)
    print("Temperature:", tcs.color_temperature)
    print("Lux:", tcs.lux)

    print()