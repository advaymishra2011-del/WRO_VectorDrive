import serial
import time

pico = serial.Serial(
    #"/dev/ttyAMA0", Check on pi
    115200,
    timeout=0.1
)

def sendCommand(MotorSpeed, Steering):
    cmd = f"{MotorSpeed},{Steering}\n"
    try:
        pico.write(cmd.encode())
    except serial.SerialException as e:
        return None
    return "Success"

def receiveData():
    try:
        msg = pico.readline().decode().strip()

        touch = list(map(int, msg.split(",")))
        if msg:
            return touch
    except serial.SerialException as e:
        return None
    return None