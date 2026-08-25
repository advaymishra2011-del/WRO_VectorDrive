import serial
import time

pico = serial.Serial(
    "/dev/serial0",
    baudrate=115200,
    timeout=1
)


def sendCommand(MotorSpeed, Steering, rot=0):
    if MotorSpeed is None:
        MotorSpeed = "None"

    if Steering is None:
        Steering = "None"

    if rot is None:
        rot = 0

    cmd = f"C,{MotorSpeed},{Steering},{rot}\n"

    try:
        pico.write(cmd.encode())
        print("PI -> PICO:", cmd.strip())
        return "Success"

    except serial.SerialException as e:
        print("SEND ERROR:", repr(e))
        return None


def receiveData():
    messages = []

    try:
        while pico.in_waiting:
            msg = pico.readline().decode(errors="replace").strip()

            if msg:
                messages.append(msg)

        return messages

    except serial.SerialException as e:
        print("RECEIVE ERROR:", repr(e))
        return None


try:
    while True:
        # Send a test command
        sendCommand(100, 90, 0)

        time.sleep(0.1)

        # Read everything Pico sent back
        data = receiveData()

        if data:
            for msg in data:
                print("PICO -> PI:", msg)
        else:
            print("PICO -> PI: NO DATA")

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
    pico.close()