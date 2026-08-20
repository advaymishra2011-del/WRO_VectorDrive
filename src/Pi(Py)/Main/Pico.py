import serial

pico = serial.Serial(
    "/dev/ttyAMA0", #Check on pi
    115200,
    timeout=0.1
)

def sendCommand(MotorSpeed, Steering, rot = 0):
    if MotorSpeed is None:
        MotorSpeed = "None"
    if Steering is None:
        Steering = "None"
    if rot is None:
        rot = 0
        
    cmd = f"C,{MotorSpeed},{Steering},{rot}\n"
    try:
        pico.write(cmd.encode())
    except serial.SerialException as e:
        return None
    return "Success"

def receiveData():
    latest = [0, 0, 0, 0, 0]

    try:
        while pico.in_waiting:

            msg = pico.readline().decode().strip()

            if not msg:
                continue

            # Rotation finished
            if msg == "D":
                latest[4] = 1
                continue

            parts = msg.split(",")

            # Touch
            if parts[0] == "T" and len(parts) == 5:
                latest[0] = int(parts[1])
                latest[1] = int(parts[2])
                latest[2] = int(parts[3])
                latest[3] = int(parts[4])

        return latest

    except (serial.SerialException, ValueError):
        return None