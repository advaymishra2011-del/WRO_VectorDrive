import serial

ser = serial.Serial(
    "/dev/serial0",
    115200,
    timeout=2
)

print("Listening...")

while True:
    data = ser.read(20)

    if data:
        print("RAW:", repr(data))