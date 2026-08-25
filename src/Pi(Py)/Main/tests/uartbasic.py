import serial
import time

ser = serial.Serial(
    "/dev/serial0",
    baudrate=115200,
    timeout=1
)

print("UART test started")

while True:
    ser.write(b"HELLO\n")

    data = ser.readline()

    if data:
        print("RX:", data.decode(errors="replace").strip())
    else:
        print("NO DATA")

    time.sleep(1)