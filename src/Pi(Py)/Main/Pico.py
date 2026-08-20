import serial

pico = serial.Serial(
    #"/dev/ttyAMA0", Check on pi
    115200,
    timeout=0.1
)

def sendCommand(MotorSpeed, Steering, rot = None):
    if MotorSpeed is None:
        MotorSpeed = 123456789
    if Steering is None:
        Steering = 123456789
    if rot is None:
        rot = 123456789
        
    cmd = f"{MotorSpeed},{Steering},{rot}\n"
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