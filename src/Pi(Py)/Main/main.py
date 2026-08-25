from Main.Algorithms import *
import statistics

turn = 75
large_buffer = 100
bufpark = 4

def getDirection():
    direction = None
    while direction is None:
        dataleft = []
        dataright = []
        for i in range(5):
            dataleft.append(getDistances(tofs)["left"])
            dataright.append(getDistances(tofs)["right"])
        lef = statistics.mean(dataleft)
        rig = statistics.mean(dataright)

        if lef<rig:
            direction = "clockwise"
        elif rig<lef:
            direction = "counterclockwise"
        else: direction = None

    distances = getDistances(tofs)
    lef1 = distances["left"]
    rig1 = distances["right"]
    while(lef1 == rig1):
        distances = getDistances(tofs)
        lef1 = distances["left"]
        rig1 = distances["right"]
        if lef1<rig1:
            direction = "clockwise"
        elif rig1<lef1:
            direction = "counterclockwise"
    return direction

def captureFrame():
    data = []
    for i in range(5):
        frame = get_frame()
        img = cv(frame)
        if img is not None:
            color = img[0]["color"]
        data.append(color)
        time.sleep(0.01)
    mode = statistics.mode(data)
    return mode

def obstacleMain(tofs, val3, speed, val, sign, turndir):
    tracker = True
    counter = 0
    while tracker:
        color = captureFrame()
        if color is None: 
            while True:
                startPid(tofs, 20, turndir, val)
                
                time.sleep(0.1)

                if captureFrame() is not None: break
                if getDistances(tofs)[turndir]   >= large_buffer:
                    tracker = False
                    break
        else:
            if counter < 2:
                obstacleAvoidance(tofs, val3, speed, val, color)
                counter += 1
            else: pass
            if getDistances(tofs)[turndir]   >= large_buffer: tracker = False
                
    turn(200, sign*25, sign*75)
    return

front_buffer = 7

def parkAlign(tofs, val3, speed, val, sign, turndir, gz_0):
    tracker = True
    counter = 0
    while tracker:
        color = captureFrame()
        if color is None: 
            while True:
                startPid(tofs, 10, turndir, val)
                
                time.sleep(0.1)

                if captureFrame() is not None: break
                if getDistances(tofs)[turndir]   >= large_buffer:
                    tracker = False
                    break
        else:
            if counter < 1:
                obstacleAvoidance(tofs, val3, speed, val, color)
                counter += 1
            else: pass
            if getDistances(tofs)[turndir]   >= large_buffer: tracker = False

    gyroPid(gz_0, 200, val4, 15)
    turn(175, sign*(-30), sign*(-180))
    frame = get_frame()
    if detect_parking(frame) is None: gyroPid(gz_0, 175, val4, None, 1)
    else: 
        parking_detected = False
        state = {
                "integral": 0,
                "last_error": 0,
                "last_time": time.monotonic()
        }
        while not parking_detected:
            frame = get_frame()
            cx = detect_parking(frame)

            distances = getDistances(tofs)
            front = distances["front"]
            main = distances[turndir]

            

            if turndir == "left":
                fake = [
                    {"color": "GREEN", "cx":cx}
                ]
                
                if cx is not None: pidcx(val3, cx, 175, "GREEN", fake, state)

                elif front <= front_buffer or receiveData()[touch_front_right] == 1:
                    interrupt("left")

            if turndir == "right":
                fake = [
                    {"color": "RED", "cx":cx}
                ]
                
                if cx is not None: pidcx(val3, cx, 175, "RED", fake, state)

                elif front <= front_buffer or receiveData()[touch_front_left] == 1:
                    interrupt("right")

            if main <= bufpark:
                sendCommand(0, 0)
                data = []
                for i in range(5):
                    data.append(getDistances(tofs)[main])
                mean = statistics.mean(data)
                if mean <= bufpark: 
                    park(turndir, sign)


def park(turndir, sign):
    stage = 1
    while True:
        startPid(tofs, 3, turndir,  val, 125)
        if getDistances(tofs)[turndir]>=18: 
            stopPid()
            startPid(tofs, 23, turndir, val, 150)
            stage = 2
        elif getDistances(tofs)[turndir] <= 3 and stage == 2:
            stopPid()
            startPid(tofs, 3, turndir, val, 125)
            stage = 3
        elif getDistances(tofs)[turndir] >= 18 and stage == 3:
            stopPid()
            gyroPid(getRot(), 150, val4, None, 4)
            turn(-200, sign*30, sign*(-180))
            wallAlign(tofs, 3, val2, 4)
            break
        time.sleep(0.01)
    return

#=========================START BUTTON==============================
from gpiozero import Button

switch = Button(5)

#=========================================================================
#==================================MAIN===================================
#=========================================================================
switch.wait_for_press()
print("Starting...")
Run = True
while Run:
    gz_0 = getRot()
    direction = getDirection()
    if(direction == "clockwise"):
        sign = 1
        turndir = "right"
    elif(direction == "counterclockwise"):
        sign = -1
        turndir = "left"

    #Exit parking
    wallAlign(tofs, 3, val2, 4)
    turn(150, sign*30, sign*90)
    turn(150, sign*(-1)*30, sign*(-1)*turn)

    for i in range(12):
        obstacleMain(tofs, val3, 200, val, sign, turndir)

    #Parallel park
    parkAlign(tofs, val3, 200, val, sign, turndir, gz_0)
        