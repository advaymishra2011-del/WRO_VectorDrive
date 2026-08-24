import serial
import time

ser = serial.Serial(
    "/dev/serial0",
    baudrate=115200,
    timeout=1
)

while True:
    ser.write(b"HELLO FROM PI\n")
    print("Sent")
    time.sleep(1)